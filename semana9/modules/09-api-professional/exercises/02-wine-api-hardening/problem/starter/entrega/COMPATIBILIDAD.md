# Compatibilidad de la API 1.1.0

La versión 1.1.0 añade `served_at`, con la fecha de atención en UTC, a la respuesta de predicción.
Este campo adicional es compatible con clientes de S7 que ignoran campos desconocidos.
Se mantienen `POST /v1/predictions`, `GET /health` y los campos públicos del contrato de S7.
El filtrado de `raw_score` retira un dato interno que no pertenecía al contrato público.
`confidence` conserva su tipo numérico y se serializa redondeado a dos decimales.
Renombrar `prediction.quality_band`, eliminar un campo público o cambiar un tipo rompería a los clientes existentes.
Un cambio incompatible requeriría una versión mayor, por ejemplo 2.0.0, y una ruta `/v2/predictions`.
Mantendría temporalmente `/v1/predictions` para permitir una migración documentada de los consumidores.
