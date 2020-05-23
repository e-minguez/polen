# Polen

WIP!

La idea es hacer scrapping de los datos de las mediciones de polen que ofrece la comunidad de Madrid, ofrecerlos en json sobre algun tipo de API rest (/polen/las_rozas/ p.ej) y twittear cuando haya algun cambio.

Todo esto con el fin de aprender algo de python, flask, etc., nada serio :)

Contribuciones bienvenidas!

## Ejemplo de json (sujeto a cambios)

```
{
    "ciudad": "Las Rozas",
    "fecha": "21-may-2020",
    "datos": [
        {
            "tipo": "Aliso",
            "medicion": "0",
            "nivel": "Bajo (< 15)"
        },
        {
            "tipo": "Artemisia",
            "medicion": "0",
            "nivel": "Bajo (< 5)"
        },
        {
            "tipo": "Cupres\u00e1ceas/Tax\u00e1ceas",
            "medicion": "13",
            "nivel": "Bajo (< 111)"
        },
        {
            "tipo": "Quenopodi\u00e1ceas/Amarant\u00e1ceas",
            "medicion": "1",
            "nivel": "Bajo (< 5)"
        },
        {
            "tipo": "Fresno",
            "medicion": "0",
            "nivel": "Bajo (< 25)"
        },
        {
            "tipo": "Aligustre",
            "medicion": "0",
            "nivel": "Bajo (< 10)"
        },
        {
            "tipo": "Olivo",
            "medicion": "57",
            "nivel": "Medio (35..69)"
        },
        {
            "tipo": "Plantago",
            "medicion": "125",
            "nivel": "Muy alto (>= 60)"
        },
        {
            "tipo": "Pl\u00e1tano de paseo",
            "medicion": "1",
            "nivel": "Bajo (< 62)"
        },
        {
            "tipo": "Gram\u00edneas",
            "medicion": "525",
            "nivel": "Muy alto (>= 161)"
        },
        {
            "tipo": "Urticaceae (Ortigas)",
            "medicion": "8",
            "nivel": "Bajo (< 10)"
        }
    ]
}
```