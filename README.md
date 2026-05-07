# Interview Notes Skill

This repository contains a Codex skill for turning interview recordings into structured Chinese study notes.

## What It Does

The `interview-notes` skill helps Codex:

- Transcribe audio files in a provided `raw` folder into same-name `.txt` files in a sibling `text` folder.
- Extract interviewer questions from transcripts.
- Generate Chinese Markdown study notes with correct, review-oriented answers.
- Keep technical proper nouns in English when appropriate, such as `Redis`, `MySQL`, `TCP`, `JVM`, and `React`.
- Remove empty note sections when no matching questions are found.

The generated notes use these categories in order:

```markdown
## 实习
## 项目
## 八股
## 其他
## 手撕
```

Only categories with questions are kept.

## Skill Layout

```text
interview-notes/
  SKILL.md
  agents/
    openai.yaml
  scripts/
    transcribe_raw.py
  README.md
  requirements.txt
```

The target interview workspace should use this data layout. The skill can live elsewhere, such as your personal Codex skills directory:

```text
some-interview-folder/
  raw/   audio recordings
  text/  transcription results, created beside raw
  note/  generated study notes, created beside raw
```

## Setup

Create a Python environment and install one Whisper backend:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`faster-whisper` is the preferred backend. The script also supports `openai-whisper` if it is installed separately.

## Transcribe Audio

Pass the folder that contains the raw audio files:

```powershell
python path\to\interview-notes\scripts\transcribe_raw.py path\to\some-interview-folder\raw
```

If this skill is installed under `.codex/skills/interview-notes`, run:

```powershell
python .\.codex\skills\interview-notes\scripts\transcribe_raw.py path\to\some-interview-folder\raw
```

Useful options:

```powershell
python path\to\interview-notes\scripts\transcribe_raw.py --raw-dir path\to\some-interview-folder\raw --model medium
python path\to\interview-notes\scripts\transcribe_raw.py --raw-dir path\to\some-interview-folder\raw --language zh
python path\to\interview-notes\scripts\transcribe_raw.py --raw-dir path\to\some-interview-folder\raw --overwrite
```

## Use The Skill

Ask Codex to use the skill:

```text
Use $interview-notes to process this raw audio folder: path/to/some-interview-folder/raw.
```

## Privacy

Audio, transcripts, and generated notes may contain private interview information. Keep `raw`, `text`, and `note` outside this skill repository or ignore them in the workspace where you process interviews.
