# Interview Notes Skill

This repository contains a Codex skill for turning interview recordings into structured Chinese study notes.

## What It Does

The `interview-notes` skill helps Codex:

- Transcribe audio files in `data/raw` into same-name `.txt` files in `data/text`.
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

The target interview workspace should use this data layout:

```text
data/
  raw/       audio recordings
  text/      transcription results
  markdown/  generated study notes
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

From a workspace that contains `data/raw`, run the script from this skill:

```powershell
python path\to\interview-notes\scripts\transcribe_raw.py --root .
```

If this skill is installed under `.codex/skills/interview-notes`, run:

```powershell
python .\.codex\skills\interview-notes\scripts\transcribe_raw.py --root .
```

Useful options:

```powershell
python path\to\interview-notes\scripts\transcribe_raw.py --root . --model medium
python path\to\interview-notes\scripts\transcribe_raw.py --root . --language zh
python path\to\interview-notes\scripts\transcribe_raw.py --root . --overwrite
```

## Use The Skill

Ask Codex to use the skill:

```text
Use $interview-notes to transcribe data/raw audio and organize data/text into Chinese Markdown study notes.
```

## Privacy

Audio, transcripts, and generated notes may contain private interview information. Keep `data/raw`, `data/text`, and `data/markdown` outside this skill repository or ignore them in the workspace where you process interviews.
