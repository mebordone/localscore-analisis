#!/usr/bin/env bash
set -euo pipefail

# Compila reports/overleaf-jaiio55-larga/main.tex con plantilla JAIIO.
# Uso:
#   ./scripts/compile-jaiio55-larga.sh
#   ./scripts/compile-jaiio55-larga.sh clean

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPORT_DIR="${WORKSPACE_ROOT}/reports/overleaf-jaiio55-larga"
MAIN_TEX="${REPORT_DIR}/main.tex"
TEMPLATE_DIR="${WORKSPACE_ROOT}/private/templates/JAIIO template overleaf"

if [[ ! -f "${MAIN_TEX}" ]]; then
  echo "Error: no se encuentra ${MAIN_TEX}" >&2
  exit 1
fi

if [[ ! -f "${TEMPLATE_DIR}/llncs.cls" ]]; then
  echo "Error: no se encuentra llncs.cls en ${TEMPLATE_DIR}" >&2
  exit 1
fi

export TEXINPUTS="${TEMPLATE_DIR}//:${TEXINPUTS:-}"

cd "${REPORT_DIR}"

if [[ "${1:-}" == "clean" ]]; then
  if command -v latexmk >/dev/null 2>&1; then
    latexmk -C main.tex
  else
    rm -f main.aux main.bbl main.bcf main.blg main.fdb_latexmk main.fls \
      main.log main.out main.run.xml main.toc
  fi
  echo "Archivos auxiliares eliminados en ${REPORT_DIR}"
  exit 0
fi

pdflatex -interaction=nonstopmode main.tex
biber main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

echo "Compilación finalizada: ${REPORT_DIR}/main.pdf"
