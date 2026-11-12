import json

from app.schemas.chat import ChatSalida, HerramientaUsada
from app.schemas.prestamo import PrestamoEntrada
from app.services.modelo import predecir

NOMBRE_TOOL = "calcular_riesgo_impago"
MAX_VUELTAS = 4

SISTEMA = (
    "Eres un asistente de riesgo de un banco. Cuando tengas todos los datos de una solicitud de "
    "prestamo, llama a la herramienta calcular_riesgo_impago. Si falta algun dato, pidelo. "
    "Nunca inventes valores. Responde en espanol y de forma breve."
)


def leer_argumentos(texto):
    """YA HECHO: convierte el texto JSON de la tool en dict ({} si no es JSON valido)."""
    try:
        datos = json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        return {}
    if isinstance(datos, dict):
        return datos
    return {}


def definir_tool() -> dict:
    return {
        "type": "function",
        "function": {
            "name": NOMBRE_TOOL,
            "description": "Calcula la probabilidad de impago de una solicitud de prestamo.",
            "parameters": PrestamoEntrada.model_json_schema(),
        },
    }


def ejecutar_tool(nombre: str, argumentos_json: str) -> dict:
    if nombre != NOMBRE_TOOL:
        return {"ok": False, "error": f"Herramienta desconocida: {nombre}"}

    argumentos = leer_argumentos(argumentos_json)
    if not argumentos:
        return {"ok": False, "error": "Argumentos JSON invalidos o vacios"}

    try:
        entrada = PrestamoEntrada.model_validate(argumentos)
        salida = predecir(entrada)
    except Exception as error:
        return {"ok": False, "error": str(error)}
    return {"ok": True, **salida.model_dump()}


def responder(mensajes, llm) -> ChatSalida:
    historial = [{"role": "system", "content": SISTEMA}]
    historial.extend(mensaje.model_dump() for mensaje in mensajes)
    herramienta_usada = None

    for _ in range(MAX_VUELTAS):
        respuesta = llm.completar(historial, [definir_tool()])
        llamadas = respuesta.get("tool_calls") or []
        if not llamadas:
            return ChatSalida(
                respuesta=respuesta.get("content") or "No he podido generar una respuesta.",
                herramienta=herramienta_usada,
            )

        historial.append(respuesta)
        for llamada in llamadas:
            funcion = llamada["function"]
            nombre = funcion["name"]
            argumentos_json = funcion["arguments"]
            resultado = ejecutar_tool(nombre, argumentos_json)
            herramienta_usada = HerramientaUsada(
                nombre=nombre,
                argumentos=leer_argumentos(argumentos_json),
                resultado=resultado,
            )
            historial.append(
                {
                    "role": "tool",
                    "tool_call_id": llamada["id"],
                    "content": json.dumps(resultado),
                }
            )

    return ChatSalida(
        respuesta="No he podido completar la solicitud. Reformula los datos e intentalo de nuevo.",
        herramienta=herramienta_usada,
    )
