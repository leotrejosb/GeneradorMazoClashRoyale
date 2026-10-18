# Clash Season Planner

Planificador de mazos de Clash Royale para un modo por temporadas donde **no se puede repetir ninguna carta
de las temporadas anteriores**. A partir del mazo que usé en la temporada 1 (mi estilo de juego), el objetivo
es proponer los mazos de las temporadas siguientes que se parezcan a ese estilo, repartiendo las cartas de
forma que ninguna temporada se quede sin piezas clave.

> **Estado del proyecto:** fase 1 (datos). Ya existe el cliente de la API oficial y un script que descarga
> cartas, perfil y batallas. El perfil de estilo, el armado de mazos y la comparación entre métodos todavía
> **no están implementados**; abajo está el plan.

## El problema

En mi modo, cada temporada se juega con un mazo distinto y una carta usada no se puede volver a elegir.
Hay 5 temporadas (5 mazos, 40 cartas distintas en total). Todas las cartas quedan entre nivel 15 y 16, así
que el nivel no sirve para decidir: lo que importa es qué **rol** cumple cada carta y cuánto se parece el
mazo nuevo a mi forma de jugar.

Mi mazo de la temporada 1: Mini P.E.K.K.A, Valquiria, Mosquetera, Montapuercos, Barril de duendes,
Mago de hielo, Princesa y Ejército de esqueletos.

## Herramientas parecidas que ya existen

Hay validadores y constructores manuales que marcan cartas repetidas entre mazos (por ejemplo, el
Deck Builder de RoyaleAPI y el planificador de guerra de TrophyCoach). Este proyecto no pretende reemplazarlos:
la idea es **proponer** los mazos automáticamente a partir de un perfil de estilo y **planificar todas las
temporadas a la vez**.

## Cómo correrlo

Requiere Python 3.9 o superior. No hay dependencias que instalar.

1. Crea una llave en [developer.clashroyale.com](https://developer.clashroyale.com). El formulario pide una
   dirección IP permitida: usa la IP pública desde la que vas a ejecutar el script.
2. Copia `.env.example` como `.env` y completa `CR_API_TOKEN` y `CR_PLAYER_TAG`.
3. Descarga los datos:

   ```
   python fetch_data.py
   ```

   (o `python fetch_data.py --tag "#TUTAG"`). Los archivos quedan en `data/raw/` y el script imprime los
   campos que trae cada respuesta.

4. Pruebas (no necesitan red ni llave):

   ```
   python -m unittest
   ```

## Estructura

```
crplanner/client.py   Cliente de la API oficial (cartas, perfil, batallas) y manejo de errores
fetch_data.py         Script que descarga y guarda las respuestas en data/raw/
tests/                Pruebas offline del cliente
data/raw/             Respuestas guardadas; cards.json sirve de respaldo para la demo sin red
```

## Seguridad

- La llave vive solo en `.env` (ignorado por git). Nunca se imprime ni se sube.
- `player.json` y `battlelog.json` están ignorados por defecto porque son datos personales.

## Plan

- [x] Cliente de la API oficial con pruebas offline
- [ ] Revisar las respuestas reales: campos de las cartas, evoluciones/campeones, alcance del registro de batallas
- [ ] Etiquetar el rol de cada carta (condición de victoria, hechizo, enjambre, etc.)
- [ ] Perfil de estilo del mazo base (elixir promedio, composición por roles)
- [ ] Reglas de mazo válido
- [ ] Método simple: armar una temporada tras otra
- [ ] Método planificado: armar todas las temporadas a la vez, y compararlo con el simple
- [ ] Pantalla simple para mostrar los mazos y su parecido al base

## Pendientes por confirmar

- Si las evoluciones y campeones cuentan como cartas aparte o repiten la carta base en este modo.
- Qué campos trae realmente `/cards` (en particular, si incluye el tipo de carta) y cuántas batallas guarda el registro.
- Cómo se vincula la llave a la IP en la página de desarrolladores.

## Limitaciones previstas

Los mazos propuestos serán coherentes con mi estilo y las reglas del modo, pero el programa no conoce el
meta actual ni cómo juego cada carta, así que no garantiza ganar.
