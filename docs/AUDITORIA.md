# Auditoría de seguridad

**Objeto:** https://github.com/Jakeschincariol/day-trader-skill
**Commit:** `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`
**Fecha:** 2 de noviembre de 2026
**Alcance:** 15.302 líneas (8.000 de Python en 11 herramientas, 1.600 de
Markdown, 57 fixtures de datos, 12 archivos de tests)
**Método:** revisión estática completa. **No se ejecutó el código.**

**Veredicto: limpio.** No se encontró código malicioso, ni puertas traseras, ni
telemetría, ni ningún mecanismo capaz de extraer datos del equipo.

---

## Resultados por vector

### Dependencias — sin superficie de ataque

Cero dependencias externas. Los únicos módulos importados son de la librería
estándar de Python:

```
argparse contextlib copy csv datetime decimal email gzip hashlib io json math
os random re shutil statistics subprocess sys tempfile time urllib xml zipfile
```

(`importlib` aparece solo en `tests/_load.py`.) Sin `pip install` no hay cadena
de suministro que comprometer, que es el vector más común en paquetes de
trading maliciosos.

### Ejecución dinámica y ofuscación — nada

Búsqueda de `eval(`, `exec(`, `__import__`, `compile(`, `pickle`, `marshal`,
`base64`, `codecs.decode`, `fromhex`, `ctypes`, `socket.`: **cero resultados**
en el código de las herramientas.

Más revelador todavía: **el repositorio no contiene ni un solo carácter
no-ASCII.** Ningún carácter de ancho cero, ninguna marca bidireccional, ningún
homoglifo. Esas son las técnicas habituales para esconder instrucciones que un
humano no ve pero un modelo de lenguaje sí lee. Aquí no hay ninguna.

### `subprocess` — un uso, legítimo

Un único punto, `trader-pelosi/ptr.py:342`:

```python
out = subprocess.run([exe, "-layout", pdf_path, "-"], capture_output=True, timeout=60)
```

Invoca `pdftotext` para leer los PDFs de declaraciones del Congreso. Lista de
argumentos (no `shell=True`), con timeout. Correcto.

### Red — solo lectura, sin salida de datos

**No existe ni una sola petición POST en todo el repositorio.** Todo el tráfico
es `urllib.request.urlopen` con peticiones GET. No hay ningún camino técnico
por el que información del equipo pueda salir hacia un servidor.

Todos los hosts están escritos en el código, no son configurables (sin riesgo
de SSRF):

| Host | Para qué |
|---|---|
| `query1/query2.finance.yahoo.com` | velas de precios |
| `feeds.finance.yahoo.com` | titulares RSS |
| `www.nasdaqtrader.com` | lista de símbolos |
| `www.sec.gov`, `data.sec.gov` | EDGAR: filings y XBRL |
| `disclosures-clerk.house.gov` | declaraciones del Congreso |
| `stooq.com` | precios de respaldo |

### Credenciales — no las toca

Lee exactamente **una** variable de entorno: `SEC_USER_AGENT` (nombre y email,
que la SEC exige para acceder a EDGAR). Nada más.

No accede a `~/.ssh`, `~/.aws`, llaveros del sistema, cookies ni perfiles de
navegador. Las claves API del broker nunca pasan por este código: van al
archivo de configuración de Claude Desktop, que lee el servidor MCP de Alpaca.
Los `SKILL.md` instruyen explícitamente a no pedirlas, no leerlas y no
repetirlas, y a decirle al usuario que regenere las claves si llega a pegar una
en el chat.

### Escrituras en disco — acotadas

Solo escribe en rutas que el usuario pasa por argumento (la carpeta `trader/`).
Usa escritura atómica vía archivo temporal. **No hay ningún borrado:** ni
`os.remove`, ni `unlink`, ni `shutil.rmtree`, ni `rm -rf`.

### Manifiesto del plugin — sin ejecución automática

`.claude-plugin/plugin.json` y `marketplace.json` **no declaran ningún hook ni
ningún servidor MCP**. Instalarlo no introduce código que se ejecute solo.
Ese es el vector por el que un plugin de Claude Code podría ejecutar algo sin
intervención, y aquí está vacío.

### Manejo de archivos comprimidos — sin zip-slip

`ptr.py:96` abre el ZIP con `io.BytesIO`, filtra los miembros `.xml` y lee el
primero **en memoria**. Nunca extrae a disco, así que no hay riesgo de
*zip-slip* (rutas `../` dentro del archivo).

Los fixtures (`2026FD.zip`, los `.gz`) se inspeccionaron: contienen únicamente
datos de mercado y un XML de declaraciones. Inofensivos.

### Inyección de prompts — ninguna, y lo contrario

Los once `SKILL.md` se revisaron buscando patrones de inyección: "ignora las
instrucciones anteriores", "no le digas al usuario", "sin preguntar",
"automáticamente", "always allow", "omite la confirmación". **Cero resultados
maliciosos.**

Lo que sí aparece, en los once archivos, son instrucciones *defensivas*
repetidas: nunca poner una herramienta de órdenes en "Always allow", nunca
pedir ni leer claves API, nunca operar desde una tarea programada "porque no
hay nadie para decir sí", nunca dos órdenes con un solo sí.

---

## La lógica de aprobación

Es la parte que importa, porque es lo único entre una idea y una orden real.
`ticket.py` **no habla con ningún broker**: solo imprime el JSON que luego
Claude pasaría al conector del broker. Las tres puertas:

1. `trader-risk` aprobó esa orden exacta hoy, emparejada por *fingerprint*.
2. El usuario escribió un "sí" explícito para esa sola orden.
3. El usuario pulsó "Allow once" en la tarjeta de permisos de Claude.

El verificador del "sí" (`ticket.py:271`) es notablemente estricto. Rechaza:

- respuestas que no empiezan por "yes"/"y" (no vale "ok", "sure", "go")
- cualquier respuesta con un `?`
- palabras de lote ("yes to all")
- palabras de duda o condición en el resto de la frase
- un "sí" que mencione otro ticker del lote
- un "sí" que mencione un número que no coincida con ninguna cifra de la orden
  (cantidad, precios, pérdida máxima)

Esto es ingeniería defensiva real, no una declaración de intenciones.

---

## Calidad del código (no es seguridad, pero importa)

- `trader-risk/check.py` (819 líneas) y `trader-budget/size.py` (881): lo mejor
  del repositorio. Aritmética en centavos enteros para evitar errores de coma
  flotante en el dinero, calendario real de festivos del NYSE, control de venta
  en corto contra las acciones realmente poseídas, acumulación del límite de
  pérdida diaria dentro del mismo lote de órdenes.
- `trader-timemachine/timemachine.py`: bootstrap IID por franja horaria, con
  semilla fija y reproducible. Desempate conservador (si una vela toca stop y
  objetivo, cuenta el stop). Metodológicamente honesto, con la limitación
  grande de que destruye la autocorrelación y la agrupación de volatilidad, lo
  cual el propio README admite.

### Honestidad del repositorio

El ejemplo con el que el pack se promociona (TSLA, 19-oct-2026) da **29,4 % de
alcanzar el objetivo frente a 25,5 % de saltar el stop**. Con un objetivo de 1R
eso es esperanza matemática negativa una vez descuentas comisiones y
*slippage*, y el README lo llama "casi una moneda al aire" en lugar de
esconderlo. Un repositorio fraudulento habría mostrado un 80 % de acierto.

Las dos afirmaciones regulatorias que hace se verificaron y son correctas:
FINRA eliminó el mínimo de 25.000 $ del *pattern day trader* (Notice 26-10,
efectiva el 4 de junio de 2026, con transición por broker hasta octubre de
2027), y el servidor MCP de Alpaca es oficial y MIT.

---

## Limitaciones de esta auditoría

Hay que decirlas, porque un informe que no las dice no sirve:

1. **Quien hizo esta revisión no ejecutó el código.** La política del entorno
   donde se hizo bloquea ejecutar código externo. El veredicto es de lectura
   estática, que es el método adecuado para buscar malware, pero la revisión en
   sí **no verificó empíricamente que los números del README se reproduzcan**.
   Esa parte la cubre ahora la CI (`.github/workflows/tests.yml`), que ejecuta
   las 315 pruebas en cada push, y `bin/trader test` en local.
2. **Un solo commit.** El historial del repositorio original está aplastado, así
   que no hay historia que auditar ni forma de ver cómo evolucionó el código.
3. **Esta auditoría cubre un commit concreto.** El autor puede cambiar cualquier
   cosa en un commit futuro. Por eso este repositorio fija
   `3d0f4ef` y guarda `docs/CHECKSUMS.txt`. Las instrucciones para actualizar
   con seguridad están en [`NOTICE.md`](../NOTICE.md).
4. **No se verificó la identidad del autor.** 4.600 estrellas y 1.100 forks
   indican popularidad, no procedencia confiable.

## Verificar la integridad en cualquier momento

```bash
bin/trader estado
# o directamente:
cd .claude/skills && sha256sum -c ../../docs/CHECKSUMS.txt
```

---

## Conclusión

El código está limpio y, en las partes que manejan dinero, está bien escrito.
**El riesgo de este repositorio no es el software: es la actividad.** El day
trading hace perder dinero a la mayoría de quienes lo practican, y nada de este
código cambia esa estadística. Lo que hace es acotar las pérdidas a cantidades
decididas de antemano y dejar un registro para entenderlas.
