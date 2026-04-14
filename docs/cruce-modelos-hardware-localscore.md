## Cruce de modelos y hardware en LocalScore (H × M) para el paper

### Propósito

Este documento sintetiza el cruce entre caracterización de hardware y caracterización de modelos para responder la pregunta central del framework:

**qué tamaños de modelo son viables en cada perfil de hardware y con qué nivel de interactividad.**

La fuente principal es `notebooks/cruce_hardware_modelos_grafico3.ipynb`, que genera:

- `reports/figures/fig03_hardware_model_perf_absolute.png`
- `reports/figures/fig03_hardware_model_perf_percent.png`
- `data/processed/fig03_hardware_model_perf_table.csv`

---

### Definiciones metodológicas usadas

#### Perfiles de hardware (H)

Se usan perfiles `H1..H7` (etiqueta corta), siguiendo la tipificación de `docs/caracterizacion-hardware-localscore.md`.

#### Perfiles de modelo (M)

Se usa la clasificación final de `docs/caracterizacion-modelos-localscore.md`:

- `M1`: `<1B`
- `M2`: `1B–4B`
- `M3`: `4B–8B`
- `M4`: `8B–16B`
- `M5`: `>16B`

#### Categorías de performance

Basadas en `avg_gen_tps`:

- **Batch**: `<10 tok/s`
- **Interactivo mínimo**: `10–25 tok/s`
- **Interactivo fluido**: `>=25 tok/s`

#### Normalización del gráfico porcentual

En `fig03_hardware_model_perf_percent.png` los porcentajes se calculan por combinación `H×M` (cada stack suma 100% dentro de su sub-barra).

---

### Cobertura del cruce analizado

El cruce parte de 1556 corridas mergeadas y analiza 1550 corridas en la figura final.  
Las 6 excluidas corresponden al perfil `H0` (no considerado en este gráfico).

#### Cobertura por hardware (N corridas)

- `H1`: 51
- `H2`: 129
- `H3`: 440
- `H4`: 70
- `H5`: 440
- `H6`: 375
- `H7`: 45

#### Cobertura por tamaño de modelo (N corridas)

- `M1`: 27
- `M2`: 743
- `M3`: 57
- `M4`: 695
- `M5`: 28

#### Cobertura por categoría de performance (global)

- **Interactivo fluido**: 943 (60.8%)
- **Interactivo mínimo**: 313 (20.2%)
- **Batch**: 294 (19.0%)

#### Cobertura de celdas H×M

- Combinaciones posibles: 35
- Con datos: 28
- Sin datos: 7 (`H1-M3`, `H1-M5`, `H4-M5`, `H5-M5`, `H7-M1`, `H7-M3`, `H7-M5`)

---

### Hallazgos principales del cruce H × M

### 1) Punto de quiebre claro entre CPU altos y GPU para modelos M4 (8B–16B)

El salto más informativo del paper aparece en `M4`:

- `H2-M4`: 100% Batch (27/27)
- `H3-M4`: 80.9% Batch, 18.6% mínimo, 0.5% fluido (183 corridas)
- `H4-M4`: 66.7% fluido (12 corridas)
- `H5-M4`: 66.4% fluido, 92.5% interactivo total (241 corridas)
- `H6-M4`: 67.8% fluido, 96.5% interactivo total (202 corridas)
- `H7-M4`: 69.2% fluido, 100% interactivo total (26 corridas)

**Interpretación:** para modelos de 8B–16B, pasar de CPU-only (`H2/H3`) a GPU (`H4+`) cambia de forma drástica la experiencia de uso.

### 2) M2 (1B–4B) se vuelve robustamente interactivo desde H3

Para `M2`:

- `H1-M2`: 47.2% interactivo total, 11.1% fluido
- `H2-M2`: 79.1% interactivo total, 38.4% fluido
- `H3-M2`: 96.0% interactivo total, 73.5% fluido
- `H4-M2`: 100% interactivo total, 85.4% fluido
- `H5/H6-M2`: ~99% interactivo total, ~94.6% fluido

**Interpretación:** el rango 1B–4B es una zona de transición donde `H2` puede servir, pero la experiencia consistente aparece desde `H3`.

### 3) El comportamiento agregado por hardware confirma gradiente de capacidad

Share de interactividad total (`mínimo + fluido`) por H:

- `H1`: 41.2%
- `H2`: 58.1%
- `H3`: 60.0%
- `H4`: 95.7%
- `H5`: 95.5%
- `H6`: 97.1%
- `H7`: 100%

**Interpretación:** hay una separación nítida entre perfiles CPU-only (`H1-H3`) y perfiles GPU/servidor (`H4-H7`).

### 4) El volumen está concentrado en dos bandas de tamaño (M2 y M4)

Las corridas del cruce se concentran en:

- `M2`: 743 corridas
- `M4`: 695 corridas

Esto es consistente con la bimodalidad observada en el documento de modelos y refuerza que las conclusiones más sólidas del paper están en esas dos bandas.

---

### Conclusiones para el paper

1. **El tamaño del modelo y el perfil de hardware interactúan de forma no lineal**: no alcanza con reportar “promedio global de tokens/s”; hay umbrales prácticos por celda `H×M`.
2. **Para 8B–16B (M4), CPU-only muestra fuerte degradación de interactividad**, mientras que GPU (`H4+`) ofrece salto sustantivo hacia uso interactivo.
3. **Para 1B–4B (M2), H3 ya permite uso interactivo estable**, y desde `H5` el comportamiento es mayormente fluido.
4. **El gráfico porcentual por `H×M` es clave** porque controla diferencias de volumen y muestra composición de experiencia por segmento.
5. **El gráfico absoluto complementa** mostrando en qué celdas la evidencia es más sólida (n alto) y dónde hay menor soporte empírico.

---

### Implicancias para recomendación (hardware × uso → modelo)

- **H1**: orientar a `M1/M2` con expectativa de batch o interacción limitada.
- **H2**: `M2` viable en uso mixto; evitar `M4` para interacción.
- **H3**: `M2` recomendado para interacción; `M4` mayormente batch.
- **H4**: primer perfil donde `M4` ya aparece mayormente fluido (con cobertura todavía moderada).
- **H5/H6**: perfiles más robustos para `M2` y `M4` interactivo/fluido.
- **H7**: desempeño alto en lo observado, pero con cobertura menor y sesgo de muestra.

---

### Limitaciones y cautelas de interpretación

1. **Sesgo de cobertura**: `H4`, `H7`, `M1`, `M3`, `M5` tienen menor muestra relativa.
2. **Celdas escasas**: hay combinaciones `H×M` con `n < 10` (ej. `H5-M1`, `H2-M1`, `H2-M5`), por lo que esos porcentajes son inestables.
3. **Combinaciones sin datos**: 7 celdas `H×M` no tienen corridas en este dump.
4. **Dependencia del dump LocalScore**: los resultados describen esta muestra (no población total de usuarios/dispositivos).

---

### Texto breve sugerido para el manuscrito

> El cruce hardware–modelo muestra un umbral estructural de interactividad: en tamaños 8B–16B (M4), los perfiles CPU-only (H2/H3) se concentran en modo batch, mientras que los perfiles con GPU (H4+) presentan mayoría de corridas interactivas y dos tercios en régimen fluido. En 1B–4B (M2), la interactividad se vuelve estable desde H3 y prácticamente plena en H5/H6. Estos resultados respaldan recomendaciones condicionadas por celda H×M, en lugar de reglas globales por tamaño de modelo.

