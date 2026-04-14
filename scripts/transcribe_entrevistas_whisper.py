#!/usr/bin/env python3
"""
Transcribe audio/video de entrevistas con Whisper (modelo large-v3, español).

Requisitos:
  - ffmpeg instalado en el sistema (Whisper lo usa para decodificar)
  - pip install faster-whisper

Uso:
  python scripts/transcribe_entrevistas_whisper.py --input docs/entrevistas/media/
  python scripts/transcribe_entrevistas_whisper.py --input ruta/video.mp4 --output salida.md

Por defecto: modelo large-v3, idioma español, salida .md junto al archivo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def find_media_files(root: Path) -> list[Path]:
    exts = {".mp4", ".webm", ".mkv", ".mov", ".m4a", ".mp3", ".wav", ".ogg", ".flac"}
    if root.is_file():
        return [root] if root.suffix.lower() in exts else []
    return sorted(
        p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts
    )


def transcribe_file(
    path: Path,
    model_size: str,
    device: str,
    compute_type: str,
    language: str,
    output_path: Path | None,
) -> str:
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        print(
            "Falta faster-whisper. Instalá con:\n"
            "  pip install faster-whisper",
            file=sys.stderr,
        )
        raise SystemExit(1) from e

    print(f"Cargando modelo Whisper: {model_size} (device={device}, compute_type={compute_type})...")
    # num_workers=1 limita VRAM en GPUs con poca memoria libre (p. ej. 12 GB con large-v3)
    model = WhisperModel(model_size, device=device, compute_type=compute_type, num_workers=1)

    print(f"Transcribiendo: {path}")
    segments, info = model.transcribe(
        str(path),
        language=language,
        beam_size=5,
        vad_filter=True,
        # Evita el loop de alucinación: no usar el texto previo como contexto del siguiente segmento
        condition_on_previous_text=False,
        # Umbral más bajo para descartar segmentos sin voz (0.6 es más agresivo que el default 0.9)
        no_speech_threshold=0.6,
    )

    lines: list[str] = []
    lines.append(f"# Transcripción: {path.name}\n")
    lines.append(f"- Idioma detectado: {info.language} (probabilidad ~{info.language_probability:.2f})\n")
    lines.append(f"- Duración aprox.: {info.duration:.1f} s\n")
    lines.append("\n---\n\n")

    for seg in segments:
        t0 = _format_ts(seg.start)
        t1 = _format_ts(seg.end)
        lines.append(f"**[{t0} → {t1}]** {seg.text.strip()}\n\n")

    text = "".join(lines)
    out = output_path or path.with_suffix(".md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"Guardado: {out}")
    return text


def _format_ts(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcripción con Whisper (alta calidad, español)")
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Archivo de audio/video o carpeta con medios",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Solo si --input es un archivo: ruta del .md de salida",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="large-v3",
        help="Modelo faster-whisper (default: large-v3). Alternativas: large-v2, medium, small",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Dispositivo (default: auto)",
    )
    parser.add_argument(
        "--compute-type",
        default="default",
        help="float16 (GPU), int8 (CPU rápido), default según device",
    )
    parser.add_argument(
        "--language",
        "-l",
        default="es",
        help="Código ISO del idioma (default: es)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"No existe: {args.input}", file=sys.stderr)
        raise SystemExit(1)

    device = args.device
    if device == "auto":
        try:
            import torch

            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"

    compute_type = args.compute_type
    if compute_type == "default":
        # int8_float16 reduce VRAM en GPU frente a float16 puro (large-v3 en ~12 GB)
        compute_type = "int8_float16" if device == "cuda" else "int8"

    files = find_media_files(args.input)
    if not files:
        print(
            "No se encontraron archivos de audio/video (.mp4, .webm, .mp3, ...).",
            file=sys.stderr,
        )
        raise SystemExit(1)

    for f in files:
        out = None
        if args.output and len(files) == 1:
            out = args.output
        transcribe_file(
            f,
            model_size=args.model,
            device=device,
            compute_type=compute_type,
            language=args.language,
            output_path=out,
        )


if __name__ == "__main__":
    main()
