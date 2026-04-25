# Análisis del benchmark LocalScore para selección de modelos en hardware local

Código y datos de soporte del paper:

> Bordone, M. (2025). *Estudio preliminar para la selección de modelos de lenguaje en hardware local: análisis del benchmark LocalScore en el marco de privacidad, acceso y soberanía computacional.* JAIIO 55 – ASAID.

## Descripción

Este repositorio contiene el análisis cuantitativo de 1556 ejecuciones del benchmark público [LocalScore](https://github.com/mozilla-ai/llamafile/tree/main/localscore) (Mozilla AI), complementado con una componente cualitativa basada en entrevistas exploratorias con tres informantes clave.

El trabajo propone perfiles operativos de hardware (H) y de tamaño de modelo (M), y un criterio de interactividad anclado en la velocidad de lectura promedio en español (Brysbaert, 2019), para orientar la selección de modelos de lenguaje en despliegue local sin requerir conocimiento técnico especializado.

## Estructura

```
├── data/
│   ├── raw/localscore-09-24-2025.db     # dump SQLite público de LocalScore (sep. 2025)
│   └── processed/                        # tablas CSV generadas por los notebooks
├── docs/                                 # notas metodológicas
├── notebooks/                            # análisis reproducibles (ver orden abajo)
├── reports/
│   ├── figures/                          # figuras generadas
│   └── overleaf-jaiio55-larga/           # paper final en LaTeX
├── scripts/
│   └── transcribe_entrevistas_whisper.py # transcripción de audio con Whisper
└── requirements.txt
```

## Reproducir el análisis

### 1. Configurar el entorno

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Ejecutar los notebooks en orden

| # | Notebook | Descripción |
|---|----------|-------------|
| 1 | `notebooks/exploracion_localscore.ipynb` | Exploración inicial del dump SQLite |
| 2 | `notebooks/caracterizacion_hardware_perfiles_localscore.ipynb` | Definición y análisis de perfiles de hardware (H0–H7) |
| 3 | `notebooks/caracterizacion_modelos_solo_localscore.ipynb` | Definición y análisis de perfiles de modelo (M1–M5) |
| 4 | `notebooks/cruce_hardware_modelos_grafico3.ipynb` | Cruce H×M×performance y generación de figuras |

Los notebooks leen desde `data/raw/localscore-09-24-2025.db` y escriben tablas procesadas en `data/processed/`.

### 3. Datos originales

El dump SQLite es un snapshot público del benchmark LocalScore tomado el 24-09-2025. La fuente original está en:
https://localscore.ai

## Datos cualitativos

Las entrevistas exploratorias con informantes clave (transcripciones y audios) no se incluyen en este repositorio por razones de privacidad. Los datos están disponibles bajo solicitud justificada dirigida al autor.

## Licencia

El código de este repositorio se distribuye bajo licencia [MIT](LICENSE).

Los datos de LocalScore son de Mozilla AI y están sujetos a su licencia original.
