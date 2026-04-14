## Caracterización de modelos en LocalScore

### Propósito

Este documento sintetiza la caracterización de modelos ejecutados en LocalScore para alimentar el framework de recomendación (**hardware × uso → modelo/configuración**). Se usa el notebook `notebooks/caracterizacion_modelos_solo_localscore.ipynb` como fuente principal.

---

### Estado de los datos: versión raw vs versión limpia (paper)

Para el paper se recomienda reportar explícitamente dos niveles:

1. **Raw (trazabilidad del dump):**
   - 1556 corridas
   - 119 modelos únicos

2. **Limpio/canonicalizado (análisis principal):**
   - 1540 corridas
   - 98 modelos únicos

La versión limpia aplica:
- canonicalización de aliases de `model_name` (ej. `Llama-3.2-1B-Instruct` → `Llama 3.2 1B Instruct`),
- filtrado de entradas basura (`.`, `..`, `active`, `hub`, `Models`, `Dir`, `Model Hf`, `Local_Pretrained_Model`),
- mapeo de familias actualizado (`QWQ → Qwen`, `MINISTRAL → Mistral`, `ExaOne → OTHER`).

**Impacto cuantitativo del cleaning:** se excluyen 16 corridas y se reduce la fragmentación por aliases.

---

### Variables utilizadas

- `model_name`
- `params`
- `model_variant_quant`
- `runtime_name`
- `avg_gen_tps`, `avg_ttft_ms`, `performance_score`
- `model_family` (inferida)
- `size_bin_params` (bins por parámetros)

**Hallazgo estructural:** 100% de corridas usan `llamafile` (1540/1540 en dataset limpio).

---

### Distribución principal (dataset limpio)

#### Por familia

| Familia | Corridas | % corridas | Modelos únicos |
|---|---:|---:|---:|
| Llama | 1015 | 65.9% | 14 |
| Qwen | 402 | 26.1% | 37 |
| Gemma | 65 | 4.2% | 17 |
| OTHER | 26 | 1.7% | 16 |
| Mistral *(incluye Ministral)* | 21 | 1.4% | 8 |
| Phi | 11 | 0.7% | 6 |

Notas:
- `Ministral` se fusiona en `Mistral` por consistencia semántica.
- `ExaOne` se agrupa en `OTHER` por baja representación (1 corrida) y criterio de agregación de minor families.

#### Por tamaño (`params`)

| Bin | Corridas | Modelos únicos | Perfil M |
|---|---:|---:|---|
| `<1B` | 26 | 9 | M1 |
| `1-2B` | 694 | 8 | M2 |
| `2-4B` | 47 | 12 | M2 |
| `4-8B` | 53 | 20 | M3 |
| `8-16B` | 692 | 31 | M4 |
| `16-32B` | 22 | 12 | M5 |
| `32-64B` | 5 | 5 | M5 |
| `>=64B` | 1 | 1 | M5 |

La muestra sigue siendo **bimodal**: picos en `1-2B` y `8-16B`.

#### Cuantización (dataset limpio)

| Cuantización | Corridas | % |
|---|---:|---:|
| Q4_K - Medium | 1329 | 86.3% |
| Q8_0 | 69 | 4.5% |
| Q6_K | 40 | 2.6% |
| Q5_K - Medium | 28 | 1.8% |
| Q4_0 | 24 | 1.6% |
| F16 | 17 | 1.1% |
| BF16 | 11 | 0.7% |
| Otras | 22 | 1.4% |

**Conclusión:** fuerte sesgo a `Q4_K - Medium` (formato dominante de distribución GGUF en llamafile).

#### Top 10 modelos por corridas (dataset limpio)

| Modelo | Familia | Corridas |
|---|---|---:|
| Llama 3.2 1B Instruct | Llama | 664 |
| Qwen2.5 14B Instruct | Qwen | 313 |
| Meta Llama 3.1 8B Instruct | Llama | 306 |
| Llama 3.2 3B Instruct | Llama | 25 |
| Gemma 3 4b It | Gemma | 17 |
| Gemma 3 1b It | Gemma | 15 |
| Mistral Nemo Instruct 2407 | Mistral | 12 |
| Qwen3 0.6B | Qwen | 12 |
| Gemma 3 12b It | Gemma | 9 |
| DeepSeek R1 Distill Llama 8B | Llama | 7 |

Los 3 primeros modelos concentran la mayor parte del volumen.

---

### Figuras del paper y su lectura

- `reports/figures/fig02a_models_bubble_family_paper.png`
  - versión principal para paper (familias: Llama, Qwen, Gemma, Mistral, Phi)
- `reports/figures/fig02a_models_bubble_family_exploratory.png`
  - versión extendida (incluye `OTHER`)
- `reports/figures/fig02b_models_top_runs.png`
  - ranking top modelos por corridas
- `reports/figures/fig02c_other_composition.png`
  - desglose interno de `OTHER`

---

### Composición de `OTHER` (nuevo análisis)

En dataset limpio:
- `OTHER`: **26 corridas**, **16 modelos**

Desglose:
- **Familias reales no mapeadas:** 16 corridas / 12 modelos
- **Alias/ambiguo:** 10 corridas / 4 modelos
- **Ruido/errores:** 0 corridas (después del cleaning)

Top familias detectadas dentro de `OTHER`:
- Granite: 6 corridas (3 modelos)
- Dria: 2 corridas (1 modelo)
- Con 1 corrida c/u: YandexGPT, WizardLM, QVikhr, OLMo, Falcon, EuroLLM, CodeGeeX, AReaL.

Implicancia: `OTHER` no es solo ruido; contiene familias reales emergentes o de nicho.

---

### Perfiles de modelo M1–M5 (vigentes)

Se mantienen los perfiles por tamaño:

- **M1:** `<1B`
- **M2:** `1B–4B`
- **M3:** `4B–8B`
- **M4:** `8B–16B`
- **M5:** `>16B`

Regla de asignación:

```text
si P < 1e9   -> M1
si P < 4e9   -> M2
si P < 8e9   -> M3
si P < 16e9  -> M4
si P >= 16e9 -> M5
```

---

### Sesgos y limitaciones (actualizado)

1. **Sesgo de runtime:** 100% llamafile; no generaliza a otros motores sin validación adicional.
2. **Sesgo de cuantización:** predominio Q4_K_M; poca cobertura de cuantizaciones altas.
3. **Concentración en pocos modelos:** alta dependencia de Llama 3.2 1B, Qwen2.5 14B y Llama 3.1 8B.
4. **Cobertura reducida en extremos:** pocos casos >16B y muy pocos <1B.
5. **Dependencia de heurística de familia:** aunque mejorada (QWQ y MINISTRAL), `OTHER` aún requiere mantenimiento periódico del diccionario.

---

### Recomendaciones para el manuscrito

- Reportar en texto principal la **versión limpia** como base inferencial.
- Incluir una nota metodológica breve con los pasos de cleaning/canonicalización.
- Usar `fig02a ... paper` como figura principal y dejar la exploratoria en anexo.
- Mantener `fig02c` para justificar que `OTHER` incluye familias reales y no solo ruido.

---

### Próximos pasos sugeridos

1. Extender el mapeo de familias para reducir `OTHER` en futuras versiones.
2. Mantener una tabla de aliases/canonicalización versionada.
3. Cruzar M × H con dataset de hardware etiquetado para reforzar recomendaciones del framework.
4. Si se amplía el dump, reevaluar umbral de inclusión de minor families (criterio por runs/modelos).
