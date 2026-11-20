# Compatibilidad con el front de S7

La API pasa de `1.1.0` a `2.0.0` porque exigir autenticación rompe a los clientes anónimos.
El formato de las predicciones y el sobre de errores mantienen el contrato anterior.
El front de S7 debe enviar `X-API-Key` en cada petición a `POST /v1/predictions`.
Debe usar la clave del cliente `front`, cuyo scope permite predecir pero no consultar `/v1/admin/usage`.
Si recibe `401`, debe revisar la configuración de la clave; si recibe `403`, los permisos.
Si recibe `429`, debe respetar `Retry-After` antes de repetir la petición.
Guardaría la clave en `st.secrets` de Streamlit o en una variable de entorno del servidor.
La clave no debe estar en el repositorio ni enviarse a código JavaScript del navegador.
El origen del front también debe figurar en `WINE_API_CORS_ORIGINS` para las llamadas desde el navegador.
