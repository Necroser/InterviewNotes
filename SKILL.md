---
name: interview-notes
description: Transcribe interview recording folders and organize interview transcripts into structured Chinese Markdown study notes with model-generated correct answers. Use when the user provides or asks to process a raw audio folder; when Codex should create sibling text and note folders beside raw; when the user asks to run local speech-to-text such as Whisper; or when the user asks to extract interviewer questions and turn them into categorized review notes for internship, project, CS fundamentals, other, and coding questions.
---

# Interview Notes

## Workflow

Use this skill for any interview data folder shaped like:

```text
some-interview-folder/
  raw/   audio recordings
  text/  transcript .txt files, created beside raw
  note/  organized Markdown study notes, created beside raw
```

Run the work in two phases:

1. Ask for or infer the `raw` folder path. Do not assume the data folders are inside the skill directory.
2. Transcribe every supported audio file in `raw` into a same-name `.txt` file in the sibling `text` folder.
3. Extract interviewer questions from each transcript in `text`, then write a same-name `.md` study-note file in the sibling `note` folder.

Preserve existing user files. Skip generated outputs that already exist unless the user asks to overwrite them.

## Phase 1: Audio To Text

Prefer the bundled script:

```bash
python interview-notes/scripts/transcribe_raw.py /path/to/raw
```

If the user gives the parent data folder that contains `raw`, use `--root`:

```bash
python interview-notes/scripts/transcribe_raw.py --root /path/to/some-interview-folder
```

Useful options:

```bash
python interview-notes/scripts/transcribe_raw.py --raw-dir /path/to/raw --model large-v3
python interview-notes/scripts/transcribe_raw.py --raw-dir /path/to/raw --overwrite
python interview-notes/scripts/transcribe_raw.py --raw-dir /path/to/raw --language zh
python interview-notes/scripts/transcribe_raw.py --raw-dir /path/to/raw --device cpu --compute-type int8 --model small
```

The script:

- Reads audio from the provided `raw` folder.
- Writes UTF-8 `.txt` files to a sibling `text` folder, creating it if needed.
- Supports common formats such as `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.aac`, `.wma`, `.mp4`, and `.mkv`.
- Tries `faster-whisper` first, then `whisper`.
- Defaults to a high-quality GPU profile: `large-v3` on CUDA with `float16`. Use `--device cpu --compute-type int8 --model small` as a slower compatibility fallback when CUDA is not available.
- On Windows, `nvidia-smi` can work while Python still cannot load CTranslate2 CUDA dependencies. If GPU mode fails with `cublas64_12.dll is not found`, tell the user to install `nvidia-cublas-cu12` and `nvidia-cudnn-cu12`, then retry with `--device cuda --compute-type float16`. The script automatically adds NVIDIA wheel DLL folders to the current process when CUDA is selected.
- Uses a local model. If model packages or model weights are missing and network access is unavailable, report the blocker and the exact command that failed.

If the project uses another local transcription tool, it is acceptable to use that tool as long as the output contract stays the same: one same-name UTF-8 `.txt` file per audio file in the sibling `text` folder.

## Phase 2: Text To Markdown Study Notes

For each `.txt` file in the sibling `text` folder, create or update the same-name `.md` file in the sibling `note` folder. Create `note` if it does not exist.

Use the transcript primarily to identify and normalize the interviewer's questions. The answer below each question should be the correct answer that Codex would recommend for review, not necessarily the answer spoken in the audio.

Write notes in Chinese. Keep necessary proper nouns, APIs, framework names, language names, database names, algorithms, and product names in English when English is the natural form, such as `React`, `Redis`, `TCP`, `B+ tree`, `MySQL`, `JVM`, `Transformer`, or `Whisper`.

Use this top-level section order:

```markdown
## 实习

---

## 项目

---

## 八股

---

## 其他

---

## 手撕
```

Only keep sections that contain at least one recovered interviewer question. If a section has no corresponding `###` questions after classification, delete that entire `##` section, including its separator. Preserve the relative order of the remaining sections.

Under each `##` section:

- Use interviewer questions as `###` headings.
- Put the answer below the `###` heading.
- Generate a correct, review-oriented answer for the question using general technical knowledge and interview best practices.
- Do not write the answer as an oral interview response. Write it as formatted study notes that are easy to review and memorize.
- Prefer bullets, numbered steps, short definitions, comparison tables, formulas, code snippets, and key takeaways when they make the answer clearer.
- For technical fundamentals, include the core concept, important details, common pitfalls, and typical follow-up points.
- For project or internship questions, use the transcript to understand the project context, then write a strong reusable answer structure. Do not invent concrete company names, metrics, architecture details, business results, or personal experience that are not present in the transcript.
- If a project or internship question lacks enough context for a factual personalized answer, write a generic but useful answer template and mark placeholders with `<...>`.
- If a question was asked but the transcript is too noisy to determine the question, skip it unless a reliable question can be recovered.
- Merge repeated or fragmented versions of the same question into one `###` heading.
- Remove small talk, greetings, scheduling, stutters, false starts, candidate mistakes, and transcription noise unless they are needed to recover the interviewer's question.
- Preserve important follow-up questions as separate `###` headings when they test different knowledge.

## Answer Style

Write answers as concise review notes:

- Start with the direct answer or definition.
- Expand with structured bullets under labels such as `核心点`、`流程`、`优缺点`、`适用场景`、`注意点`、`复杂度`、`追问`.
- Use tables for comparisons, such as TCP vs UDP, process vs thread, B+ tree vs B tree, or MySQL indexes.
- Use fenced code blocks for hand-written coding questions when useful.
- Keep paragraphs short. Avoid filler such as `我觉得`、`然后`、`这个问题的话`、`大概就是`.
- Prefer reusable memory hooks, but do not add exaggerated mnemonics or unrelated explanations.

## Classification Rules

Put content in the first matching section:

- `实习`: internship experience, company work, team collaboration, production tasks, business impact, resume internship details.
- `项目`: personal projects, course projects, competition projects, system design around the user's project, project difficulties and optimizations.
- `八股`: standard CS or engineering fundamentals, such as OS, networking, database, Java/C++, JVM, distributed systems, Redis, MySQL, algorithms concepts, browser, frontend, machine learning basics.
- `手撕`: coding-by-hand questions, algorithm implementation, SQL writing, code debugging, complexity analysis tied to a concrete programming problem.
- `其他`: self-introduction, motivation, school/career plans, behavioral questions, salary/location/timing, questions to interviewer, or anything that does not fit above.

If a question combines categories, choose the section that matches the interviewer's main intent. For example, "你项目里 Redis 怎么用，为什么这样设计" goes to `项目`; "Redis 持久化有哪些方式" goes to `八股`; "现场写 LRU cache" goes to `手撕`.

## Output Quality

Use compact Markdown:

```markdown
## 项目

### 你的项目里为什么要引入 Redis？

核心作用：

- 缓存热点数据，降低数据库压力。
- 承担高频读写场景，提升接口响应速度。
- 支持分布式锁、限流、排行榜、计数器等业务能力。

注意点：

- 缓存一致性：常见方案是先更新数据库，再删除缓存。
- 缓存穿透：使用参数校验、空值缓存或 Bloom Filter。
- 缓存雪崩：设置随机过期时间，避免大量 key 同时失效。

---
```

Do not add extra first-level titles unless the user asks for an index or combined report. For a single transcript, the file content should start with the first non-empty `##` section in the required order.

Before finishing, check:

- Every remaining `##` heading is non-empty and appears in the required order.
- Empty categories are removed entirely.
- Questions are `###` headings.
- Answers are correct, structured study notes rather than transcript-faithful oral responses.
- Answers are Chinese with necessary English proper nouns preserved.
- The Markdown file is saved under the sibling `note` folder with the same base name as the source `.txt`.
