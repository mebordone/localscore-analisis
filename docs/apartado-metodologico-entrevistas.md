## Apartado metodológico (entrevistas) — estudio preliminar ASAID

### Diseño

Se realizó un **relevamiento cualitativo exploratorio** mediante **entrevistas semiestructuradas** a **informantes clave** (*key informants*) con el objetivo de caracterizar (i) **necesidades y prácticas** de uso de LLMs y (ii) **restricciones socio-técnicas** asociadas al despliegue local (hardware, privacidad, accesibilidad), y así derivar requisitos traducibles a métricas de rendimiento para el cruce con datos de benchmarking.

El enfoque se diseñó explícitamente para capturar tanto la perspectiva del individuo (“**yo**”, prácticas concretas) como una lectura del colectivo (“**nosotros**”, variabilidad y barreras observadas en colegas), reconociendo que esta segunda capa constituye **percepción experta** y no estimación representativa.

### Casos e informantes

Se seleccionaron tres casos por **muestreo intencional** debido a su experiencia, rol de coordinación y capacidad de análisis crítico (no tecnooptimista):

- **Caso docente**: docente universitario/a (tecnología educativa y artes), con experiencia de coordinación de docencia para cohortes numerosas; evaluaciones frecuentes basadas en textos; conectividad institucional (wifi).
- **Caso investigador social**: investigador/a en sociología de la técnica (software libre e IA libre), con trabajo sobre entrevistas, redes, textos y encuestas; alta sensibilidad frente a privacidad; uso de R y Python; coordinación de una diplomatura en IA para ciencias sociales.
- **Caso desarrollador**: SRE en cooperativa, experiencia en sistemas complejos (incl. bancarios) y stack open source; automatización con Ansible y exploraciones en IoT; restricciones potenciales de seguridad/compliance.

### Instrumento

Se elaboró una guía de entrevista **semiestructurada** con espacio para derivaciones, organizada en cinco bloques: consentimiento, contexto de trabajo, walkthrough de una tarea concreta, métricas humanas (traducibles a métricas técnicas), restricciones (privacidad/soberanía/accesibilidad) y lectura del colectivo. Para mantener comparabilidad entre casos, se utilizó una **guía común** y se desarrollaron guías complementarias por perfil:

- `docs/entrevistas/guia-comun.md`
- `docs/entrevistas/guia-caso-docente.md`
- `docs/entrevistas/guia-caso-investigador-social.md`
- `docs/entrevistas/guia-caso-desarrollador.md`

Como soporte de registro y síntesis se definió una **ficha de salida** (1 página) para completar al finalizar cada entrevista, incluyendo: top de tareas, inputs/outputs típicos, idioma(s), sensibilidad de datos, hardware declarado y rangos de requisitos.

### Procedimiento de recolección

- **Duración**: 30–45 minutos por entrevista.
- **Modalidad**: preferentemente videollamada.
- **Registro**: grabación de audio con consentimiento explícito, con propósito de toma de notas.
- **Anonimización**: reporte de resultados a nivel “caso” (docente / investigador social / desarrollador), sin nombres ni instituciones.

Durante cada entrevista se priorizó:

1. Un **walkthrough** (paso a paso) de una tarea real o típica.
2. La identificación de **tolerancias humanas** (p. ej., “me corta el flujo” vs “puedo esperar”) para su posterior traducción.
3. Un bloque final “nosotros” para captar **heterogeneidad intra-perfil** (sub-perfiles, barreras típicas, condiciones de adopción).

Para aumentar robustez interpretativa ante generalizaciones sobre “el colectivo”, se aplicó una regla sistemática: ante cada afirmación general sobre colegas se solicitó **un ejemplo concreto** y **un contraste** (“quiénes lo viven distinto y por qué”).

### Perfiles de hardware (relevamiento y tipificación)

Para conectar los relatos de uso con la factibilidad técnica de ejecución local, el estudio releva **hardware existente** y lo organiza en **perfiles de referencia**. El relevamiento se realiza en dos niveles:

1. **Hardware declarado del informante** (micro): equipo(s) efectivamente disponibles para su trabajo cotidiano (CPU, RAM, presencia/tipo de GPU y VRAM si aplica, sistema operativo), además de restricciones del entorno (p. ej., red cerrada, sin internet, disponibilidad de soporte).
2. **Hardware típico del colectivo** (meso): percepción del informante clave sobre qué configuraciones son comunes, cuáles son excepcionales (“lujo”), y qué infraestructura institucional podría existir (p. ej., servidor).

Como base para el cruce con LocalScore y para el prototipo de recomendación, se emplean **cinco perfiles de hardware**:

- **H1 — CPU-only muy bajo**: laptop/notebook sin GPU dedicada, RAM muy acotada (p. ej., entre 2 y <8 GB).  
  - **Riesgo**: es probable que esté fuertemente subrepresentado en LocalScore; se incluye por relevancia para docencia/estudiantes y como objetivo de estudios específicos.
- **H2 — CPU-only bajo**: laptop/notebook sin GPU dedicada, RAM acotada pero más habitual (p. ej., 8–16 GB).
- **H3 — CPU-only medio**: desktop/laptop sin GPU dedicada pero con más RAM/CPU (p. ej., 16–32 GB o más), apto para batch o tareas menos interactivas.
- **H4 — GPU (VRAM moderada)**: GPU dedicada con VRAM típica 6–16 GB, orientada a usos interactivos y modelos medianos cuantizados.
- **H5 — GPU alta gama**: GPU dedicada con VRAM típica ≥ 24 GB, orientada a modelos mayores, mayor throughput y menor restricción de cuantización.
- **H6 — Servidor institucional**: infraestructura compartida (CPU/RAM altas y/o GPU(s) dedicadas), útil para despliegues locales compartidos cuando el hardware personal no alcanza o se requiere consolidar recursos.

Estos perfiles se usan como categorías de comparación entre casos y se ajustan según información emergente. La intención es que el framework pueda: (i) recomendar para hardware existente y (ii) aportar orientación básica de “si tuvieras un monto X, qué upgrade conviene” como extensión, sin que la decisión de compra sea el foco central del estudio preliminar.

### Operacionalización: de métricas humanas a métricas técnicas

El objetivo no fue imponer umbrales técnicos a priori, sino **derivarlos** desde el relato de uso. Sin embargo, para conectar entrevistas con benchmarking (LocalScore) se definieron correspondencias operativas entre respuestas “humanas” y rangos técnicos:

- **Interactividad (TTFT)**: la tolerancia a la espera de “primera respuesta” se traduce a rangos de TTFT (p. ej., interrupción del flujo \(\rightarrow\) ~1–2 s; tolerable \(\rightarrow\) ~2–5 s; modo batch \(\rightarrow\) >5–10 s).
- **Velocidad sostenida (tokens/s de generación)**: la necesidad de iteración rápida vs modo batch se traduce a rangos de *throughput* (p. ej., rápido ~25–50 tok/s; medio 10–25 tok/s; lento aceptable 2–10 tok/s).
- **Necesidad de contexto**: la longitud típica de inputs (número de páginas, documentos o turnos) se utiliza para estimar demanda de ventana de contexto y/o necesidad de RAG local.
- **Riesgo de alucinación/confianza**: el “costo” percibido de error (bajo/medio/alto) se codifica como criterio de selección de modelo/modo (p. ej., priorizar trazabilidad/citas, restricciones de uso, o mayor intervención humana).

Estas traducciones se registran en la ficha de salida para cada caso y se incorporan luego en el entrecruzamiento “uso × hardware × configuración de modelo”.

### Análisis y síntesis

El análisis se orienta a producir artefactos comparables entre casos, más que a saturación teórica:

1. **Síntesis por caso**: lista priorizada de tareas, restricciones, y requisitos (rangos).
2. **Tipologías dentro del colectivo**: sub-perfiles y barreras de adopción (descriptivo).
3. **Requisitos traducibles** para el cruce con LocalScore: TTFT, tokens/s y necesidad de contexto/documentos.

El resultado esperado de esta fase es un conjunto de **perfiles de uso** que alimenten:

- la definición de tipos de uso para el paper,
- los umbrales mínimos por uso,
- y el prototipo de recomendación (p. ej., árbol de decisión) como resultado preliminar.

### Consideraciones éticas y limitaciones

Las entrevistas son reportadas de forma **anonimizada** y orientadas a prácticas generales; no obstante, dada la naturaleza de informantes clave, se asume que parte del valor proviene de su experiencia de coordinación, lo cual introduce sesgos posibles (p. ej., visión “desde arriba” del colectivo). Por ello:

- No se infieren proporciones poblacionales ni representatividad estadística.
- La capa “nosotros” se interpreta como **percepción experta** contextual.
- Los resultados se usan para proponer **criterios y rangos** (no reglas universales).

En futuras iteraciones se prevé ampliar la muestra o triangular con observación de uso y/o evaluación de tareas, según disponibilidad y tiempo.

