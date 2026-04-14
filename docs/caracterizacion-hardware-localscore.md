## Caracterización de hardware en LocalScore (para perfiles y recomendación)

### Propósito

Este documento resume cómo caracterizar el **hardware** disponible en el dump de LocalScore y qué **variables** conviene usar para **agrupar** configuraciones en perfiles interpretables (orientados a despliegue local de LLMs). El objetivo final es poder:

- derivar perfiles de hardware realistas para docentes, investigadores y desarrolladores,
- comparar rendimiento entre grupos,
- y alimentar el futuro framework de recomendación (hardware × uso → modelo/configuración).

Se asume que algunos grupos relevantes para el doctorado (p. ej., **CPU-only bajo**) pueden estar **subrepresentados** en LocalScore; aun así se mantienen en la tipificación para guiar estudios posteriores y recolección dirigida de datos.

---

### Qué hay en el notebook y qué implica para hardware

En `notebooks/exploracion_localscore.ipynb` se trabaja principalmente con la tabla **agregada**:

- `accelerator_model_performance_scores`

Esta tabla resume métricas por combinación (acelerador, modelo, cuantización/variante), e incluye un campo clave:

- `accelerator_memory_gb`

En el análisis preliminar se observa el siguiente rango (desde `df.describe()`):

- **mínimo**: 2.0 GB  
- **p25**: ~15.2 GB  
- **mediana**: ~24.0 GB  
- **p75**: ~59.4 GB  
- **máximo**: ~755.8 GB

**Interpretación importante:** en GPU, `accelerator_memory_gb` suele aproximar **VRAM**, pero para CPU el “acelerador” puede representar el host (o un recurso no estrictamente equiparable a VRAM). Por eso, para caracterizar **CPU-only** conviene apoyarse en tablas de sistema (RAM/CPU) además de esta variable.

---

### Por qué una caracterización completa requiere más tablas (no solo `accelerator_model_performance_scores`)

Para una tipificación de hardware alineada a “lo que tienen las personas” se necesita separar al menos:

- **sistema/host** (CPU, RAM, OS),
- **acelerador** (GPU/CPU como dispositivo de cómputo, y su memoria),
- **runtime** (software usado para correr la inferencia),
- **configuración de modelo** (variante/cuantización),
- **resultado de performance** (TTFT, tokens/s, etc.).

En el dump de LocalScore, esto se reconstruye mejor con la tabla de corridas y catálogos:

- `benchmark_runs` (métricas por corrida y vínculos a sistema/acelerador/modelo/runtime)
- `benchmark_systems` (CPU, arquitectura, RAM, kernel/versión)
- `accelerators` (nombre, tipo, memoria, fabricante)
- `model_variants` y `models` (modelo base y cuantización)
- `runtimes` (motor de inferencia y versión)
- `test_results` (resultados más finos por test; útil si se quieren métricas adicionales como power o VRAM usada)

**Consecuencia:** para agrupar “hardware” de forma sólida, lo recomendable es construir un dataset “largo” a partir de `benchmark_runs` y sus joins a `benchmark_systems` + `accelerators` + `runtimes` + `model_variants/models`.

---

### Variables recomendadas para agrupar hardware (features de perfil)

Una caracterización orientada a perfiles (y que luego sirva en un árbol de decisión simple) puede separar variables en tres capas: **host**, **acelerador** y **entorno**.

#### 1) Host (persona / máquina)

Desde `benchmark_systems`:

- `cpu_arch` (x86_64, arm64, etc.)
- `cpu_name` (familia/modelo)
- `ram_gb` (RAM disponible)
- `kernel_type`, `kernel_release`, `system_version` (para compatibilidad)

**Clave para CPU-only:** `ram_gb` es la variable central para perfilar capacidad de ejecutar modelos cuantizados en CPU (junto con `cpu_arch` por optimizaciones SIMD/NEON/AVX).

#### 2) Acelerador (si existe)

Desde `accelerators`:

- `type` (CPU vs GPU)
- `memory_gb` (VRAM o memoria del dispositivo)
- `manufacturer` (NVIDIA/AMD/Apple/etc.)
- `name` (para agrupar en “familias” o “tiers”)

**Nota Apple Silicon:** LocalScore registra el mismo chip dos veces: una entrada con `type=GPU` (cluster GPU/Metal, `memory_gb` = memoria unificada total) y otra con `type=CPU` (cluster CPU, misma `memory_gb`). Las corridas de inferencia usan el backend Metal; la entrada relevante es la de tipo GPU. En consecuencia, **todos los equipos Apple Silicon se clasifican en H4–H6** según su memoria unificada, nunca en H0–H3.

#### 3) Entorno de ejecución

Desde `runtimes`:

- `name` (motor: llama.cpp, vLLM, etc.)
- `version` (y commit si existe)

Aunque runtime no es “hardware”, afecta fuertemente la performance y puede ser una variable de control o estratificación en comparativas.

---

### Propuesta de perfiles H0–H7 (tipos de hardware)

Se definen ocho perfiles de hardware para clasificar configuraciones de despliegue local de LLMs. Los cortes se eligen en potencias de 2 (RAM) y en discontinuidades reales del mercado de GPUs (VRAM), no en valores arbitrarios.

| Perfil | Tipo | Rango | Incluye | No incluye |
|--------|------|-------|---------|------------|
| **H0** | CPU-only | RAM < 4 GB | Edge devices, Raspberry Pi, equipos muy viejos, IoT | Cualquier laptop mainstream; prácticamente **ausente en LocalScore** |
| **H1** | CPU-only | 4 GB ≤ RAM < 8 GB | Laptops de entrada (4 u 8 GB), Chromebooks con RAM extra | Equipos < 4 GB (H0) o ≥ 8 GB (H2) |
| **H2** | CPU-only | 8 GB ≤ RAM < 16 GB | Laptops Intel/AMD sin GPU discreta (8–16 GB RAM) | Equipos con GPU dedicada; Equipos con GPU dedicada o acelerador Apple Silicon (siempre en H4–H6 vía tipo GPU) |
| **H3** | CPU-only | RAM ≥ 16 GB | Desktops de trabajo, laptops high-end (16–64 GB+), servidores CPU-only | Cualquier equipo con GPU discreta habilitada |
| **H4** | GPU consumer | VRAM < 8 GB | GTX 1650 4 GB, GTX 1660 6 GB, RTX 3050 laptop 6 GB | GPU con ≥ 8 GB (H5/H6); GPUs datacenter (H7) |
| **H5** | GPU consumer | 8 GB ≤ VRAM < 24 GB | RX 6600 8 GB, Apple M1/M2 8 GB (mem. unificada), RTX 3080 10 GB, RTX 4060 Ti 16 GB, RTX 4080 16 GB, RX 7900 XT 20 GB, Apple M2 Pro 16 GB | RTX 3090/4090 con 24 GB (H6); datacenter (H7) |
| **H6** | GPU consumer high-end | VRAM ≥ 24 GB | RTX 3090 24 GB, RTX 4090 24 GB, Apple M4 Max 128 GB, workstations personales | GPUs datacenter como A100/H100 aunque tengan > 24 GB (→ H7) |
| **H7** | Servidor/datacenter | Por nombre de GPU (prioridad absoluta sobre rangos de VRAM) | A100, H100, H200, V100, L40S, MI300X, Tesla, Gaudi; infraestructura institucional compartida | Uso personal; GPUs consumer aunque sean potentes (→ H6) |

#### Algoritmo de asignación (implementado en `caracterizacion_hardware_perfiles_localscore.ipynb`)

La asignación de perfil se basa en **dos variables primarias**: `accelerator_type` (CPU/GPU) y, según el tipo, `ram_gb` del sistema host o `memory_gb` del acelerador.

```
dado un benchmark_run:

si accelerator_type = "CPU":
    leer ram_gb (desde benchmark_systems)
    si ram_gb <  4   → H0_CPU_EDGE   # intervalo [0,  4)  — excluye 4
    si ram_gb <  8   → H1_CPU_LOW    # intervalo [4,  8)  — incluye 4, excluye 8
    si ram_gb < 16   → H2_CPU_MED    # intervalo [8, 16)  — incluye 8, excluye 16
    si ram_gb >= 16  → H3_CPU_HIGH   # intervalo [16, ∞)  — incluye 16

si accelerator_type = "GPU":
    si nombre del acelerador contiene keyword datacenter
                     → H7_SERVER     # PRIORIDAD ABSOLUTA — se evalúa antes que VRAM
    si memory_gb es nulo → UNKNOWN
    si memory_gb <  8   → H4_GPU_LOW   # intervalo [0,  8)  — excluye 8
    si memory_gb < 24   → H5_GPU_MED   # intervalo [8, 24)  — incluye 8, excluye 24
    si memory_gb >= 24  → H6_GPU_HIGH  # intervalo [24, ∞)  — incluye 24

si accelerator_type es nulo o desconocido → UNKNOWN
```

**Keywords datacenter (H7):** `H100, H200, A100, A40, L40S, MI250, MI300, MI300X, TESLA, V100, P100, A800, GAUDI, SERVER EDITION, BLACKWELL SERVER`  
La comparación se hace en mayúsculas sobre el campo `accelerators.name`. Esta lista cubre los aceleradores de datacenter más comunes en el dump; no es exhaustiva y puede extenderse.

**Nota sobre Apple Silicon:** LocalScore registra el mismo chip Apple Silicon **dos veces** en el catálogo `accelerators`: una entrada `type=GPU` con `memory_gb` igual a la memoria unificada total (usada para inferencia con Metal), y otra `type=CPU` con la misma `memory_gb` (corridas en modo CPU puro). Para las corridas de inferencia acelerada, `accelerator_type = "GPU"` y la memoria unificada entra como `memory_gb`; el equipo cae en **H4–H6** según ese valor.

**Limitación conocida:** la memoria unificada es el límite total del sistema — no hay RAM de host adicional, a diferencia de una GPU discreta. Un equipo Apple Silicon del mismo tier VRAM es más restrictivo en la práctica.

Ejemplos: Mac Air M1 8 GB → **H5** (8 ∈ [8, 24)); Mac Studio M4 Max 128 GB → **H6** (128 ∈ [24, ∞)).

**Nota sobre iGPU (Intel/AMD integrada):** si no hay GPU discreta, LocalScore registra el acelerador como CPU. Estos equipos caen en H0–H3 según `ram_gb`.


#### Justificaciones para el paper

**Cortes de RAM (H0–H3) en potencias de 2:**
Los módulos DIMM de RAM se comercializan en capacidades de 2, 4, 8 y 16 GB; los equipos reales tienen configuraciones que son múltiplos de estos valores. El umbral de 4 GB (H0/H1) corresponde al mínimo práctico para cargar en memoria un modelo de 1B parámetros con cuantización Q4 (~500 MB de modelo + ~1–2 GB de overhead del runtime). Los umbrales de 8 GB (H1/H2) y 16 GB (H2/H3) coinciden con los puntos de inflexión donde es posible ejecutar modelos de 7B y 13B respectivamente con cuantizaciones Q4/Q8.

**Cortes de VRAM (H4–H6) en 8 y 24 GB:**
El umbral de 8 GB (H4/H5) es la frontera entre poder correr un modelo de 7B con Q4 (≈4.5 GB de modelo) con margen suficiente o no. El umbral de 24 GB (H5/H6) corresponde a la discontinuidad real del mercado consumer: no existen GPUs de consumo masivo entre 16 y 24 GB (el salto es RTX 4080 16 GB → RTX 3090/4090 24 GB), lo que hace que 24 GB sea un corte natural y no arbitrario.

**Separación H6 (GPU consumer high-end) vs H7 (servidor/datacenter):**
La distinción no se basa en VRAM, sino en el **contexto de uso y el diseño del hardware**:
- H6 son GPUs consumer usadas en workstations personales o de laboratorio (una sola persona, uso interactivo, sin multi-tenancy). Ejemplo: RTX 4090 de 24 GB o Mac Studio M4 Max.
- H7 son aceleradores diseñados para racks de datacenter con alta densidad, refrigeración especial, multi-tenancy y acceso compartido (A100, H100, V100, MI300X). Un A100 de 40 GB en un servidor institucional no es equivalente funcional a un RTX 4090 de escritorio, aunque ambos tengan > 24 GB.
- La clasificación se opera mediante heurística por nombre de modelo (lista `DATACENTER_KEYWORDS`) en el notebook. Un Apple M4 Max de 128 GB de memoria unificada personal va a H6; un A100 de 40 GB en un clúster va a H7.

**Cobertura real en LocalScore (dump sept. 2024, N=1556 corridas):**
- H0 (6), H4 (70): baja representación; LocalScore no cubre bien edge ni GPUs muy pequeñas.
- H1 (51), H2 (129), H3 (440): cobertura creciente con el nivel; H1/H2 subrepresentados respecto al parque real de usuarios tipo docente/investigador.
- H5 (440), H6 (375): bien cubiertos; equipos de entusiastas y workstations son el perfil típico de quien envía benchmarks.
- H7 (45): baja cobertura; los servidores institucionales rara vez publican benchmarks.

---

### ¿Qué queda fuera de LocalScore?

- **H0 completo**: edge, IoT, móviles — LocalScore no tiene soporte para esos dispositivos.
- **Memoria unificada (Apple Silicon)**: NO queda fuera de la clasificación — se captura en H4–H6 vía `type=GPU`. **Limitación conocida:** la memoria unificada es el límite total del sistema (sin RAM de host separada), lo que hace que un equipo Apple Silicon sea más restrictivo que una GPU discreta del mismo tier. Ver nota detallada en la sección del algoritmo de asignación.
- **CPU + GPU integrada** (iGPU en Intel/AMD): el benchmark los registra como CPU si no hay GPU discreta. Se clasifican como H0–H3 según RAM.
- **Restricciones de entorno** (red cerrada, sin permisos de instalación, drivers faltantes): no son capturables desde el dump; se documentan en el análisis cualitativo.
- **Clusters distribuidos**: fuera del alcance de LocalScore (un nodo = una corrida).

---

### Implicancias para el framework de recomendación

El framework opera con entradas:

1. **Perfil de hardware** (H0–H7) o valores crudos (RAM, VRAM, CPU arch).
2. **Tipo de uso** (derivado de entrevistas: interactividad, longitud de output, tolerancia a errores, necesidad de documentos).

Y produce: modelo + cuantización + runtime + modo (CPU/GPU/servidor).

Reglas orientativas por perfil:
- **H0–H1**: derivar a solución cloud/servidor (H7) o limitarse a modelos 1B Q4 con expectativas muy bajas.
- **H2–H3**: modelos 7B Q4/Q8 para uso interactivo; 13B Q4 para batch.
- **H4**: modelos 3–7B Q4, uso interactivo lento.
- **H5**: modelos 7–13B Q4/Q8 interactivos; 34B Q4 en batch.
- **H6**: modelos 13–70B Q4/Q8 sin restricciones fuertes.
- **H7**: sin restricción de tamaño; priorizar throughput y multi-usuario.

---

### Próximos pasos sugeridos

1. Construir dataset unido: `benchmark_runs` + `benchmark_systems` + `accelerators` + `runtimes` + `model_variants/models`.
2. Aplicar reglas de asignación H0–H7 (`benchmark_systems.ram_gb` para CPU; `accelerators.memory_gb` + keywords para GPU).
3. Verificar cobertura por perfil y registrar sesgos (H0 y H1 son los más subrepresentados; H4 y H7 tienen cobertura baja pero no nula).
4. Planificar recolección dirigida para H0–H1 si son relevantes para el público objetivo del estudio.

