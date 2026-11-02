# Cómo operar con esto

La forma óptima de usar este repositorio no es la que parece. Lo escribo aquí
porque el error más caro es empezar por el paso 10.

## Fase 0: no operes (primeras semanas)

Suena absurdo, pero es donde está el valor real, y es gratis.

```bash
bin/trader estado
bin/trader test
```

Luego, cada día, haz el recorrido completo **sin conectar ningún broker**:

```bash
bin/trader universo
bin/trader escanear --at 10:15
bin/trader noticias TSLA
bin/trader salida --stop or-mid --target 1R
bin/trader simular
bin/trader tamano
bin/trader riesgo
bin/trader ticket
```

Al final tendrás un ticket en pantalla que no va a ninguna parte. Perfecto.
Apunta en un archivo qué habría pasado: a qué precio habría entrado, si habría
tocado el stop o el objetivo, y cuánto habrías ganado o perdido.

**Haz esto 30 sesiones antes de conectar nada.** Si después de 30 días tu
registro está en negativo, ya has aprendido lo que querías saber y te ha
costado cero euros. Eso es el mejor resultado posible de este repositorio.

## Fase 1: papel (meses, no semanas)

Solo ahora conecta Alpaca en papel, siguiendo
[`.claude/skills/trader-broker/SKILL.md`](../.claude/skills/trader-broker/SKILL.md).

El ciclo completo de una operación, en orden. Cada paso lee el archivo que
escribió el anterior:

### 1. Encuentra el candidato

```bash
bin/trader universo                   # una vez al día, antes de abrir
bin/trader escanear --at 10:15
```

La ventana por defecto de tu configuración no deja entrar antes de las 10:00 ni
después de las 15:00 (hora de Nueva York). Los primeros 30 minutos son los más
caros para aprender: el spread es ancho y los movimientos son ruido.

### 2. Entiende por qué se mueve

```bash
bin/trader noticias TSLA
```

Si no hay ninguna razón detrás del movimiento, es ruido. Y si la razón son
resultados trimestrales **esta semana**, piénsalo dos veces: un día de
resultados puede hacer cualquier cosa que no esté en los datos históricos, y
por tanto tampoco está en la simulación.

### 3. Confirma que el setup está activado

```bash
bin/trader entrada TSLA
bin/trader vigilar TSLA --every 30    # si quieres que vigile por ti
```

`esperando` significa esperando. No lo fuerces.

### 4. Fija la salida ANTES de entrar

```bash
bin/trader salida --stop or-mid --target 1R
```

Este es el paso que no se salta nunca. Si no sabes dónde vas a salir, no sabes
cuánto estás arriesgando, y entonces el resto del cálculo es ficción.

### 5. Mira las probabilidades honestas

```bash
bin/trader simular
```

Te va a dar tres números: objetivo primero, stop primero, y seguir abierto al
cierre. **Si el objetivo no gana claramente al stop, no operes.** El ejemplo
que trae el propio pack da 29,4 % frente a 25,5 %: eso no es una operación,
es una moneda al aire con comisiones en contra.

Recuerda lo que es esta simulación: sortea velas pasadas de forma
independiente. Destruye la tendencia real del mercado y no sabe nada de
resultados trimestrales ni de halts. Es un chequeo de realidad, no una
probabilidad.

### 6. Deja que el programa calcule el tamaño

```bash
bin/trader tamano
```

No redondees el número hacia arriba. El tamaño sale de tu pérdida máxima
dividida por el riesgo por acción. Si salen 3 acciones, son 3 acciones.

### 7. Pasa el control de riesgo

```bash
bin/trader riesgo
```

**Si dice BLOCK, el día ha terminado para esa idea.** No cambies la
configuración para que pase. Ese impulso, el de editar `config.json` para que
el programa te deje hacer lo que ya habías decidido hacer, es exactamente lo
que este repositorio existe para frenar. Si cedes a eso, has convertido una
herramienta de disciplina en un generador de justificaciones.

### 8. Lee el ticket y decide tú

```bash
bin/trader ticket
```

Luego, en el chat: `/trader-broker`. Claude te enseñará el ticket, tú escribes
"sí" para esa sola orden, y después pulsas "Allow once".

El verificador del "sí" es estricto a propósito: rechaza "ok", "dale", "sí a
todo", cualquier respuesta con un condicional, y cualquier "sí" que mencione un
ticker o una cantidad distinta de la del ticket. No intentes convencerlo.

### 9. Mientras está abierta

```bash
bin/trader alertas-crear
bin/trader alertas
```

Las órdenes del bracket (stop y objetivo) ya están en el broker y se cancelan
entre sí. Las alertas son tu red de seguridad, no el mecanismo.

### 10. Fuera antes del cierre

Tu `flat_by` son las 15:50 de Nueva York. Un day trade se cierra el mismo día,
siempre. Dejar una posición abierta de un día para otro convierte una operación
de day trading en algo completamente distinto, con un riesgo nocturno que no
has calculado y que ningún stop cubre si abre con gap.

### 11. Registra el resultado

```bash
bin/trader registro
```

Esto es lo que alimenta tu límite de pérdida diaria y tu recuento de
operaciones. Si no registras los resultados, el control de riesgo trabaja
con datos falsos y te deja hacer más de lo que deberías.

## Fase 2: dinero real (opcional, y probablemente no)

Antes de cambiar `"paper": false`, contesta estas cuatro preguntas por escrito:

1. ¿Cuántas sesiones llevo en papel? Si son menos de 100, la respuesta es no.
2. ¿Cuál es mi resultado acumulado en papel, después de restar una comisión
   realista y un *slippage* realista en cada operación?
3. ¿Cuántas veces he editado `config.json` para que una operación pasara el
   control de riesgo? Si la respuesta no es cero, el problema no es el software.
4. ¿Puedo perder todo el `budget` sin que cambie nada en mi vida?

En papel no hay slippage, no hay órdenes que no se ejecutan, y no hay el pulso
que se te acelera cuando el número es real. Un buen resultado en papel no
predice un buen resultado real; es solo el requisito mínimo para tener derecho
a plantearse la pregunta.

Si decides hacerlo: empieza con una fracción de lo que tenías en papel, no con
el total.

## Los errores que cuestan dinero

- Editar `config.json` para que una orden pase el control de riesgo.
- Entrar en los primeros 30 minutos "porque se está moviendo mucho".
- No registrar las operaciones perdedoras, con lo que el límite diario nunca
  se activa.
- Mover el stop a peor "para darle margen". Un stop movido no es un stop.
- Añadir a una posición que va en contra.
- Operar un día de resultados trimestrales con una simulación construida sobre
  días normales.
- Dejar una posición abierta de un día para otro.
- Pedirle a Claude que "lo haga todo" y aprobar tickets sin leerlos.
- Poner una herramienta de órdenes en "Always allow" porque las
  confirmaciones molestan.

## Y lo que hay que tener presente siempre

La mayoría de quienes hacen day trading pierden dinero. Este repositorio no
cambia eso: solo hace que, si pierdes, pierdas cantidades que decidiste de
antemano, y que tengas un registro para entender por qué.

El mejor uso posible de todo esto es llegar, después de 30 sesiones en seco, a
la conclusión de que no vale la pena. Esa conclusión es gratis aquí, y cara en
el mercado.
