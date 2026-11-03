# trade

Mi estación de trabajo para operar acciones de EE.UU. con Claude: once
herramientas que escanean gráficos, leen noticias y filings, calculan el stop
y el objetivo, simulan el resultado antes de arriesgar un dólar, y bloquean
cualquier operación que se salga de mis límites.

Basado en [Jakeschincariol/day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill)
(MIT), auditado antes de instalarlo. Detalles en [NOTICE.md](NOTICE.md) y
[docs/AUDITORIA.md](docs/AUDITORIA.md).

---

## Lo primero, para que no haya malentendidos

**Este repositorio no puede comprar ni vender nada.** No es una limitación que
haya que configurar: es lo que hace el código. La única herramienta que habla
de órdenes, `ticket.py`, nunca se conecta a un broker. Solo imprime en pantalla
el texto de la orden. Para que una orden llegue al mercado tienen que pasar
tres cosas, **cada vez**:

1. El gestor de riesgo aprueba **esa orden exacta** ese mismo día.
2. Tú escribes "sí" en el chat, para **esa sola orden**.
3. Tú pulsas **"Allow once"** en la tarjeta de permisos de Claude.

Sin esas tres, no hay orden. No hay modo automático. No hay "opéralo por mí
mientras duermo", y las propias skills prohíben operar desde tareas programadas
"porque no hay nadie para decir sí".

**Por defecto opera en papel** (`"paper": true`), con dinero simulado.

Y el dato que importa más que todo el código: **la mayoría de quienes hacen
day trading pierden dinero.** Esto no te da ninguna ventaja sobre el mercado.
Te da disciplina, aritmética correcta y un registro. Nada más.

---

## El panel

Si prefieres ver el proceso en vez de leer salidas de terminal:

```bash
bin/trader panel
```

Levanta un servidor local y abre [`index.html`](index.html), un tablero que lee los archivos
que escriben las herramientas y te muestra dónde estás en el recorrido, el plan actual, las
probabilidades, la orden propuesta y el veredicto de riesgo. Incluye una calculadora de
tamaño que funciona sin datos, una checklist antes de dar tu «sí», y un diario para las 30
sesiones en seco.

El panel **solo lee**: no se conecta a ningún broker, no tiene tus claves y no existe ningún
botón que envíe una orden. No carga nada de internet, y la CI lo comprueba en cada push.

## Empezar en 4 pasos

### 1. Comprueba que todo está en su sitio

```bash
bin/trader estado
```

Verifica tu Python, lee tu configuración, cuenta las once skills y comprueba
con SHA-256 que el código sigue siendo idéntico al que audité.

### 2. Ejecuta las pruebas

```bash
bin/trader test
```

Corren sin red, sobre datos reales congelados (las velas de 5 minutos de TSLA
de 60 días, el escaneo de las 10:15, los filings reales de la SEC). Si pasan,
la aritmética que va a dimensionar tus posiciones funciona.

Las mismas 315 pruebas corren en GitHub Actions en cada push
([`.github/workflows/tests.yml`](.github/workflows/tests.yml)), en Python 3.9,
3.11 y 3.13, junto con la verificación SHA-256 del código importado. Así que si
alguna vez alguien toca una de las once herramientas, salta en el PR.

### 3. Pon tus números

Abre [`trader/config.json`](trader/config.json) y edítalo. **Los valores que
vienen son deliberadamente diminutos**: 1.000 $ de presupuesto, 10 $ de pérdida
máxima por operación, 2 operaciones al día. Es un punto de partida seguro, no
una recomendación.

Lo que más importa, en orden:

| Clave | Qué es | Viene |
|---|---|---|
| `budget` | Con cuánto operas en total | `1000` |
| `max_loss_per_trade_usd` | Lo máximo que pierdes si salta el stop | `10` |
| `max_daily_loss_usd` | Si lo alcanzas, se cierra el día | `20` |
| `max_trades_per_day` | Freno al *revenge trading* | `2` |
| `min_reward_risk` | Ratio mínimo beneficio/riesgo para entrar | `1.5` |
| `paper` | `true` = simulado. **Déjalo así.** | `true` |

Si vas a usar las skills de la SEC (`analista`, `noticias`, `congreso`), la SEC
exige identificarse: pon tu nombre y tu email en `sec_user_agent`. Si lo haces,
revisa [NOTICE.md](NOTICE.md#tu-email-y-este-repositorio) antes de hacer commit.

### 4. Aplica los permisos (opcional pero recomendado)

```bash
cp docs/permisos-ejemplo.json .claude/settings.json
```

Y borra a mano las líneas que empiezan por `//` (JSON no admite comentarios).
Deja las once herramientas en `allow` para no confirmar cada comando, y **todas
las herramientas de órdenes de tu broker en `ask`**. Esa es la línea que de
verdad te protege.

---

## Cómo se usa

### Desde el chat de Claude

Las once skills están en `.claude/skills/`, así que en este proyecto Claude las
descubre solas y las invocas por su nombre:

```
/trader-scanner      /trader-news        /trader-entry       /trader-exit
/trader-timemachine  /trader-budget      /trader-risk        /trader-broker
/trader-alerts       /trader-analyst     /trader-pelosi
```

O simplemente pídelo en lenguaje normal: *"escanea rupturas del rango de
apertura"*, *"¿qué noticias hay de TSLA hoy?"*, *"calcula el tamaño de la
posición"*.

### Desde la terminal

```bash
bin/trader flujo          # te lleva paso a paso por una operación completa
bin/trader ayuda          # todos los comandos
```

Los comandos, en el orden en que se usan:

```bash
bin/trader universo                 # ~5.900 acciones de EE.UU. (una vez al día)
bin/trader diario                   # setups pre-mercado en todo el universo
bin/trader escanear --at 10:15      # rupturas del rango de apertura hasta esa hora
bin/trader noticias TSLA            # titulares, 8-K y el movimiento de hoy
bin/trader entrada TSLA             # esperando / activado / expirado
bin/trader vigilar TSLA             # vela a vela hasta que se active
bin/trader salida                   # stop y objetivo, ANTES de entrar
bin/trader simular                  # 10.000 replays + el histórico del setup
bin/trader tamano                   # cuántas acciones caben en tu límite
bin/trader riesgo                   # PASS / BLOCK contra tus límites
bin/trader ticket                   # el ticket en lenguaje claro
bin/trader alertas-crear            # alertas de stop, objetivo y cierre
bin/trader alertas                  # suena lo que haya tocado
bin/trader analista TSLA            # trimestres, crecimiento, beneficio
bin/trader congreso                 # operaciones declaradas por el Congreso
```

El orden no es decorativo: cada paso lee el archivo que escribió el anterior,
en la carpeta `trader/`.

```
escanear → noticias → entrada → salida → simular → tamano → riesgo → ticket
```

**La guía completa de cómo operar está en
[docs/COMO-OPERAR.md](docs/COMO-OPERAR.md).** Léela antes de la primera vez.

---

## Las once herramientas

| Comando | Qué hace |
|---|---|
| `/trader-scanner` | Escanea miles de gráficos buscando setups: rupturas del rango de apertura, banderas, rebotes de sobreventa. |
| `/trader-news` | Titulares y 8-K de cada acción que sigues, y qué la está moviendo. |
| `/trader-entry` | Vigila un setup vela a vela y te dice el momento exacto de entrar. |
| `/trader-exit` | Fija el stop y el objetivo **antes** de entrar. |
| `/trader-timemachine` | Replay del resto de la sesión 10.000 veces, más todas las veces que el setup se activó en el pasado. |
| `/trader-risk` | PASS o BLOCK de cada orden contra tus límites, con el motivo. |
| `/trader-budget` | Dimensiona la posición según tu presupuesto y tu pérdida máxima. |
| `/trader-broker` | Monta el ticket y te lo enseña. **Nunca envía nada solo.** |
| `/trader-alerts` | Avisa en el stop, en el objetivo y a las 15:50 para cerrar. |
| `/trader-analyst` | Lee los resultados trimestrales y resume qué cambió. |
| `/trader-pelosi` | Las operaciones que declara el Congreso de EE.UU. (público, no información privilegiada). |

---

## Conectar un broker (solo cuando llegue el momento)

No hace falta ningún broker para usar casi todo este repositorio. Escanear,
simular, calcular tamaños y ver tickets funciona sin conectar nada, y es ahí
donde está el 90 % del valor.

Cuando quieras operar en papel de verdad, la ruta está documentada paso a paso
en [`.claude/skills/trader-broker/SKILL.md`](.claude/skills/trader-broker/SKILL.md):
el servidor MCP oficial de Alpaca (`alpacahq/alpaca-mcp-server`, MIT), con
claves **de papel**, en el archivo de configuración de Claude Desktop, nunca en
el chat.

Tres reglas que no se negocian:

- Claves de papel, separadas de las reales. Si alguna vez pegas una clave en un
  chat, bórrala y genera claves nuevas en el panel de Alpaca.
- `place_stock_order` en **"Needs approval"**. Nunca en "Always allow". Nunca.
- Opciones, cripto, margen, venta en corto, `close_all_positions` y
  `cancel_all_orders`: **bloqueados**.

---

## Lo que esto no arregla

Lo escribo aquí para acordarme cuando se me olvide:

- **Los datos son frágiles.** El endpoint de gráficos de Yahoo Finance no es una
  API oficial: puede retrasarse, cambiar o limitarte sin avisar. Lee velas de 1
  y 5 minutos, no ticks. Contrasta con el broker cualquier cosa que importe.
- **La Time Machine es una simulación, no una predicción.** Sortea velas pasadas
  de forma independiente, lo que destruye la tendencia y la agrupación de
  volatilidad del mercado real. No modela resultados trimestrales, halts ni
  gaps. Es un chequeo de realidad, no una probabilidad fiable.
- **Un stop es un plan, no una garantía.** En un mercado rápido o en un gap, se
  ejecuta mucho peor que su precio. La pérdida máxima que ves es la pérdida *al
  precio del stop*.
- **Ninguna ventaja estadística.** Ruptura del rango de apertura, banderas,
  rebote de sobreventa: son los patrones más conocidos y explotados del trading
  minorista. El propio ejemplo que trae el pack da 29,4 % de acierto frente a
  25,5 % de stop: casi una moneda al aire.
- **Solo mercado de EE.UU.** NYSE/Nasdaq, SEC, festivos de EE.UU., hora de Nueva
  York. Para acciones europeas no sirve.
- **Meter un modelo de lenguaje en el bucle añade un modo de fallo nuevo.** Si
  Claude lee mal un número al montar el ticket, los tres filtros ayudan, pero
  el último filtro eres tú, leyendo con prisa en mitad de la sesión.

---

## Estructura

```
README.md                    esto
index.html                   el panel visual (bin/trader panel)
NOTICE.md                    procedencia, licencia y qué se modificó
.github/workflows/tests.yml  CI: las 315 pruebas + verificación de integridad
LICENSE                      MIT, de Jake Schincariol
bin/trader                   el lanzador (nunca envía órdenes)
trader/config.json           tus límites  <-- EDÍTALO
.claude/skills/trader-*/     las once skills, código sin modificar
tests/                       la suite completa + fixtures reales
docs/COMO-OPERAR.md          la guía de uso
docs/AUDITORIA.md            el informe de seguridad
docs/CHECKSUMS.txt           SHA-256 de cada archivo original
docs/permisos-ejemplo.json   permisos recomendados para .claude/settings.json
docs/README-original-en.md   el README original en inglés
```

---

## Letra pequeña

**Esto no es asesoramiento financiero.** Es software que lee datos públicos y
hace aritmética. No conoce mi situación y no puede ver el futuro. Un PASS del
gestor de riesgo es una comprobación de reglas, no una recomendación.

Las ganancias de day trading son ganancias a corto plazo, y operar con
frecuencia hace probables las *wash sales*. Nada de esto es asesoramiento
fiscal. Para España, consulta a un asesor: el tratamiento no es el de EE.UU.

Código original MIT © Jake Schincariol. Esta adaptación mantiene la misma
licencia.
