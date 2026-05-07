#!/usr/bin/env python
"""Batch transcribe a raw audio folder into sibling text UTF-8 txt files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


AUDIO_EXTENSIONS = {
    ".aac",
    ".flac",
    ".m4a",
    ".mkv",
    ".mp3",
    ".mp4",
    ".ogg",
    ".wav",
    ".wma",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe audio files in a raw folder to same-name .txt files in its sibling text folder."
    )
    parser.add_argument(
        "raw_dir",
        nargs="?",
        help="Folder containing raw audio files. The sibling text folder is created automatically.",
    )
    parser.add_argument(
        "--raw-dir",
        dest="raw_dir_option",
        help="Folder containing raw audio files. Overrides the positional raw_dir argument.",
    )
    parser.add_argument(
        "--root",
        help="Deprecated compatibility option: project root containing data/raw and data/text.",
    )
    parser.add_argument("--text-dir-name", default="text", help="Sibling folder name for transcripts.")
    parser.add_argument("--model", default="small", help="Whisper model size or local model path.")
    parser.add_argument("--language", default="zh", help="Language code passed to Whisper. Use auto for detection.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing transcript files.")
    parser.add_argument(
        "--device",
        default="auto",
        help="Device for faster-whisper, such as auto, cpu, cuda. openai-whisper ignores auto.",
    )
    parser.add_argument(
        "--compute-type",
        default="auto",
        help="Compute type for faster-whisper, such as auto, int8, float16, float32.",
    )
    return parser.parse_args()


def discover_audio(raw_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in raw_dir.iterdir()
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    )


def build_faster_whisper(model_name: str, device: str, compute_type: str):
    from faster_whisper import WhisperModel

    kwargs = {}
    if device != "auto":
        kwargs["device"] = device
    if compute_type != "auto":
        kwargs["compute_type"] = compute_type
    model = WhisperModel(model_name, **kwargs)

    def transcribe(audio_path: Path, language: str) -> str:
        lang = None if language == "auto" else language
        segments, _info = model.transcribe(str(audio_path), language=lang, vad_filter=True)
        return "".join(segment.text.strip() + "\n" for segment in segments).strip() + "\n"

    return transcribe


def build_openai_whisper(model_name: str, device: str):
    import whisper

    kwargs = {}
    if device != "auto":
        kwargs["device"] = device
    model = whisper.load_model(model_name, **kwargs)

    def transcribe(audio_path: Path, language: str) -> str:
        kwargs = {"fp16": False}
        if language != "auto":
            kwargs["language"] = language
        result = model.transcribe(str(audio_path), **kwargs)
        return result["text"].strip() + "\n"

    return transcribe


def get_transcriber(model_name: str, device: str, compute_type: str):
    faster_error = None
    try:
        return "faster-whisper", build_faster_whisper(model_name, device, compute_type)
    except Exception as exc:  # noqa: BLE001 - preserve original import/model-load failures for diagnostics.
        faster_error = exc

    try:
        return "openai-whisper", build_openai_whisper(model_name, device)
    except Exception as whisper_error:  # noqa: BLE001
        raise RuntimeError(
            "Could not initialize faster-whisper or openai-whisper.\n"
            f"faster-whisper error: {faster_error}\n"
            f"openai-whisper error: {whisper_error}\n"
            "Install one local backend, for example: pip install faster-whisper"
        ) from whisper_error


def main() -> int:
    args = parse_args()
    if args.raw_dir_option:
        raw_dir = Path(args.raw_dir_option).resolve()
    elif args.raw_dir:
        raw_dir = Path(args.raw_dir).resolve()
    elif args.root:
        raw_dir = (Path(args.root).resolve() / "data" / "raw")
    else:
        raw_dir = (Path.cwd() / "raw").resolve()

    text_dir = raw_dir.parent / args.text_dir_name

    if not raw_dir.exists():
        print(f"Missing raw audio directory: {raw_dir}", file=sys.stderr)
        return 2
    text_dir.mkdir(parents=True, exist_ok=True)

    audio_files = discover_audio(raw_dir)
    if not audio_files:
        print(f"No supported audio files found in {raw_dir}")
        return 0

    pending = []
    for audio_path in audio_files:
        output_path = text_dir / f"{audio_path.stem}.txt"
        if output_path.exists() and not args.overwrite:
            print(f"skip existing: {output_path.name}")
            continue
        pending.append((audio_path, output_path))

    if not pending:
        print("All transcripts already exist.")
        return 0

    backend_name, transcribe = get_transcriber(args.model, args.device, args.compute_type)
    print(f"Using {backend_name} model={args.model}")

    for index, (audio_path, output_path) in enumerate(pending, start=1):
        print(f"[{index}/{len(pending)}] transcribing: {audio_path.name}")
        text = transcribe(audio_path, args.language)
        output_path.write_text(text, encoding="utf-8")
        print(f"wrote: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
