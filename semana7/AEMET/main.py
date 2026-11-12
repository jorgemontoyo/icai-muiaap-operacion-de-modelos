import os
import requests

api_key = os.getenv("AEMET_API_KEY")
if not api_key:
    raise RuntimeError("No encuentro AEMET_API_KEY en esta terminal.")

url = (
    "https://opendata.aemet.es/opendata/api/"
    "valores/climatologicos/inventarioestaciones/todasestaciones"
)

respuesta = requests.get(url, params={"api_key": api_key}, timeout=30)
print("Estado de la petición:", respuesta.status_code)
respuesta.raise_for_status()

# La primera respuesta contiene un enlace para descargar el inventario.
enlace_datos = respuesta.json().get("datos")
if not enlace_datos:
    raise RuntimeError(f"La respuesta no contiene el enlace 'datos': {respuesta.text}")

respuesta_datos = requests.get(enlace_datos, timeout=30)
print("Estado de descarga del inventario:", respuesta_datos.status_code)
respuesta_datos.raise_for_status()

estaciones = respuesta_datos.json()
estacion = next(
    (
        e for e in estaciones
        if e.get("nombre", "").strip().upper() == "MADRID, CIUDAD UNIVERSITARIA"
    ),
    None,
)

if estacion:
    idema = estacion["indicativo"]
    print("Estación:", estacion["nombre"])
    print("Indicativo (idema):", idema)

    fecha_ini = "2019-10-01T00:00:00UTC"
    fecha_fin = "2019-10-30T23:59:59UTC"

    # Codificamos los dos puntos de la fecha para incluirla en la ruta.
    from urllib.parse import quote

    url_climatologia = (
        "https://opendata.aemet.es/opendata/api/"
        "valores/climatologicos/diarios/datos/"
        f"fechaini/{quote(fecha_ini, safe='')}/"
        f"fechafin/{quote(fecha_fin, safe='')}/"
        f"estacion/{idema}"
    )

    respuesta_clima = requests.get(
        url_climatologia,
        params={"api_key": api_key},
        timeout=30,
    )
    print("Estado de la petición de climatología:", respuesta_clima.status_code)
    respuesta_clima.raise_for_status()

    # AEMET devuelve otro enlace; lo usamos para descargar los datos.
    enlace_clima = respuesta_clima.json().get("datos")
    if not enlace_clima:
        raise RuntimeError(
            f"La respuesta no contiene el enlace 'datos': {respuesta_clima.text}"
        )

    respuesta_datos_clima = requests.get(enlace_clima, timeout=30)
    respuesta_datos_clima.raise_for_status()
    print(respuesta_datos_clima.text)
else:
    print("No encontré esa estación. Revisa los nombres disponibles.")