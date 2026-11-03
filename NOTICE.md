# Procedencia y cambios

## De dónde sale este código

Las once skills de `.claude/skills/` vienen de:

- **Repositorio:** https://github.com/Jakeschincariol/day-trader-skill
- **Commit exacto:** `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`
  (*"The Trader skill v2: 11 day-trading skills"*)
- **Autor:** Jake Schincariol
- **Licencia:** MIT (ver [`LICENSE`](LICENSE), conservada sin modificar)
- **Importado el:** 2 de noviembre de 2026

El README original en inglés se conserva íntegro en
[`docs/README-original-en.md`](docs/README-original-en.md).

## Qué se modificó

**El código de las herramientas: nada.** Los 8.000 largos de Python de las once
skills y los 57 fixtures de los tests son byte a byte idénticos al original.
Verificable en cualquier momento:

```bash
cd .claude/skills && sha256sum -c ../../docs/CHECKSUMS.txt
```

O contra el repositorio original directamente:

```bash
git clone https://github.com/Jakeschincariol/day-trader-skill /tmp/upstream
cd /tmp/upstream && git checkout 3d0f4ef
for d in /ruta/a/trade/.claude/skills/trader-*; do
  diff -r "/tmp/upstream/$(basename "$d")" "$d"
done
```

Se modificaron **exactamente dos archivos**, los dos de la suite de pruebas, y
solo porque las carpetas han cambiado de sitio:

### 1. `tests/_load.py`

El original asume que las once carpetas `trader-*` están en la raíz del
repositorio. Aquí viven en `.claude/skills/`, que es donde Claude Code
descubre las skills de un proyecto. El cambio son tres rutas:

```python
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(REPO, ".claude", "skills")   # antes: REPO
FIX  = os.path.join(REPO, "tests", "fixtures")
```

La función `load()` es idéntica.

### 2. `tests/test_repo.py`

Dos aserciones comprobaban la disposición literal de carpetas del repositorio
original, y por tanto fallaban con la nueva:

- `test_root_matches_the_reel` ahora comprueba que `.claude/skills/` contiene
  exactamente el manifiesto y las once carpetas de skills, y que `LICENSE`,
  `README.md`, `tests/`, `bin/` y `docs/` existen en la raíz.
- `test_readme_carries_the_reel_copy` lee el README original en su nueva
  ubicación, `docs/README-original-en.md`, en vez de la raíz.

Las otras 10 pruebas de ese archivo, y los otros 11 archivos de tests, están
sin tocar. Siguen comprobando lo importante: que las once skills llevan el
bloque de seguridad, que la cuenta de papel es el valor por defecto, que
`require_stop`, `allow_margin` y `allow_short` son los correctos, y que todo
corre en Python 3.8.

## Qué se añadió

Nada de esto existe en el original. Es la capa en español, y no toca la lógica
de trading:

| Archivo | Qué es |
|---|---|
| `README.md` | Guía de entrada en español |
| `NOTICE.md` | Este archivo |
| `index.html` | Panel visual que lee los archivos de `trader/`. Solo lectura, sin red, sin botones de orden. Se abre con `bin/trader panel` |
| `bin/trader` | Lanzador con comandos en español. **No puede enviar órdenes:** solo ejecuta las herramientas de lectura y cálculo |
| `trader/config.json` | Configuración lista para usar, con límites deliberadamente pequeños |
| `.gitignore` | Para que el registro de operaciones, las claves y los `.env` no acaben publicados |
| `.github/workflows/tests.yml` | CI: ejecuta las 315 pruebas en Python 3.9/3.11/3.13 y verifica los SHA-256 del código importado en cada push |
| `docs/COMO-OPERAR.md` | La guía de uso paso a paso |
| `docs/AUDITORIA.md` | El informe de la revisión de seguridad |
| `docs/CHECKSUMS.txt` | SHA-256 de los 29 archivos originales |
| `docs/permisos-ejemplo.json` | Permisos recomendados para `.claude/settings.json` |
| `docs/README-original-en.md` | El README original, conservado |

## Este repositorio es público y tiene GitHub Pages

Dos hechos que conviene tener presentes, comprobados el 3 de noviembre de 2026:

- `javi-molin/trade` es **público** (`"visibility": "public"`).
- **GitHub Pages está activo** y publica el repositorio en
  `https://javi-molin.github.io/trade/`. El panel responde HTTP 200 ahí, y
  también lo hace `trader/config.json`.

Decisión tomada: `trader/config.json` **sigue versionado**, para que el
repositorio funcione recién clonado. Eso significa que tu presupuesto y tus
límites de riesgo son públicos. Son cifras, no secretos, y es una elección
consciente.

Lo que **no** debe acabar ahí es tu identidad para la SEC. Va en la variable de
entorno, que tiene prioridad sobre el archivo:

```bash
export SEC_USER_AGENT="Tu Nombre tu@email.com"
```

Tres cosas sostienen esa decisión:

1. El valor que trae el archivo es `Tu Nombre you@example.com`. Las
   herramientas detectan `you@example.com` como marcador y lo rechazan en vez
   de mandarlo a la SEC (`facts.py:57`, `news.py:60`).
2. `bin/trader estado` dice de dónde está leyendo la identidad y avisa si
   viene del archivo público.
3. La CI falla si alguna vez aparece una identidad real en
   `trader/config.json`.

Lo que **nunca** se publica, porque `.gitignore` lo excluye: el registro de
decisiones (`trader/state/`), tu cartera, las órdenes, los planes y las
alertas. Verificado: `trader/state/risk.json` da 404 en la URL pública.

Si algún día prefieres que nada de esto sea público, las dos salidas son poner
el repositorio en privado o desactivar Pages, las dos en los ajustes de GitHub.

## Si quieres actualizar desde el original

El autor podría cambiar cualquier cosa en un commit futuro, y el historial del
repositorio original está aplastado en un solo commit, así que no hay historia
que auditar. No actualices a ciegas:

1. Clona el original en una carpeta aparte.
2. `diff -r` contra `.claude/skills/` y **lee el diff completo**, no solo el
   resumen. Presta atención a cualquier `POST`, `subprocess`, `eval`, `base64`,
   host nuevo, o cambio en la lógica de aprobación de `ticket.py`.
3. Si te convence, copia y regenera los checksums:
   ```bash
   cd .claude/skills && find . -type f | sort | xargs sha256sum > ../../docs/CHECKSUMS.txt
   ```
4. `bin/trader test` antes de volver a operar.
