import requests

API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqbW9udG95by5zb2xlckBnbWFpbC5jb20iLCJqdGkiOiI3YTVhMjUwYS01ZWFiLTQwZmYtOGNhOC05YTcxM2FkZTE4MTEiLCJleHAiOjE4MDEyNDc4MTgsImlzcyI6IkFFTUVUIiwiaWF0IjoxNzkyNjA3ODE4LCJ1c2VySWQiOiI3YTVhMjUwYS01ZWFiLTQwZmYtOGNhOC05YTcxM2FkZTE4MTEiLCJyb2xlIjoiIn0.VqPK1YXicCxlIu9wpQ189mOacWD8LA0ftDggAjD5B74"

url_inventario = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones"
IDEMA = "EL_INDICATIVO_QUE_ENCONTRASTE"
url = (
    "https://opendata.aemet.es/opendata/api/valores/"
    "climatologicos/diarios/datos/"
    "fechaini/2019-10-01T00:00:00UTC/"
    "fechafin/2019-10-30T23:59:59UTC/"
    f"estacion/{IDEMA}"
)

respuesta = requests.get(
    url_inventario,
    params={"api_key": API_KEY}
)

response = respuesta.json()

url_datos = requests.get(response["datos"])
response_datos = url_datos.json()
print(response_datos)
