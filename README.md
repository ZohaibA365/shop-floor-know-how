# Manufacturing Knowledge Capture

An interview demo app. Veterans talk through a job, AI drafts a step-by-step work instruction, a supervisor approves it, and new hires get answers **only** from approved instructions, with the source shown. If nothing approved covers a question, the app says "Ask your lead" and logs it as a gap to capture next.

Demo client: **Grand River Fabrication (fictional)**, a 45-person sheet metal shop in Cambridge, Ontario.

## Setup (once)

```bash
cd shop-floor-know-how
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then put your key in .env: ANTHROPIC_API_KEY=...
```

The first launch downloads the speech-to-text model (faster-whisper `base.en`, about 140 MB) into `models/`. Launch the app once before the interview so the download is already done.

## Run

```bash
streamlit run app.py
```

Opens at http://localhost:8501.

## Reset

Restores the clean demo state: the start-of-shift check approved, no BR-220 instruction, and a seeded question log.

- In the app: sidebar → **Demo controls** → **Reset demo**
- From the terminal: `python reset_demo.py`

## Eval

```bash
python eval.py
```

Runs 15 questions (10 answerable, 5 not covered) against the start-of-shift and backup BR-220 instructions loaded straight from `demo_data/seed.json`, so the live demo state doesn't affect results. It prints answers correct out of 10, "Ask your lead" replies correct out of 5, and whether every safety question included its safety note word for word. The lockout question must be answered from BR-220.

## Demo checklist (under 3 minutes)

**Before the call**
1. Run `python reset_demo.py`, then `streamlit run app.py`.
2. Browser zoom at 110 to 125 %. Close other tabs.
3. Optional dry run: do the flow below once, then press **Reset demo**.
4. Fallback: if live drafting fails, open **Demo controls** → turn on **Load backup BR-220** and go straight to Ask.

**Live flow**
1. **1. The Problem** (20 sec): the headline, the three cards, the value table (≈ $27,600/year vs ≈ $1,200 to run), the Release 1 scope line.
2. Sidebar → **Veteran · Dave** → **Use sample transcript** → **Create draft**. Wait for the spinner, then point out the transcript and the counts.
3. **Go to Review & Approve as Priya** → edit one step (e.g. add "(rev C)" to the job sheet step). Point out the yellow "please confirm" items and the red safety notes → **Approve and publish** → "Approved. Now visible to new hires."
4. **Open the Ask page as Jordan** → click **"My bend is coming out at 92 degrees, what do I do?"** → answer with the source line (by Dave, approved by Priya).
5. Click **"Can I skip lockout if I'm just swapping the punch quickly?"** → "No." plus the red safety box, word for word.
6. Click **"How do I set up the laser cutter?"** → "I don't have an approved instruction for this. Ask your lead."
7. Sidebar → **Supervisor · Priya** → **Unanswered questions** tab → the laser cutter question is at the top under "Gaps to capture next".
8. **5. Pilot Plan & Metrics** (50 sec): timeline, live KPIs (approved count, helpful %, questions per new hire), training, guardrails, roadmap. User stories stay collapsed unless asked.

## How it works

| Piece | File |
|---|---|
| App shell, sidebar, role switcher, demo controls | `app.py` |
| Pages | `views/problem.py`, `capture.py`, `review.py`, `ask.py`, `pilot.py` |
| Claude calls, prompts, strict JSON + one retry | `core/llm.py` |
| Ask pipeline + code-side checks (source must be approved, safety note shown word for word) | `core/ask.py` |
| SQLite storage | `core/db.py` (database at `data/app.db`) |
| Seed data and reset | `core/seed.py`, `demo_data/seed.json`, `demo_data/dave_br220.txt` |
| Speech-to-text (local, loads at startup) | `core/transcribe.py` |

Guardrails in code:
- Drafts are never sent to the Ask model. Only `approved` instructions are, and the backup BR-220 only when the toggle is on.
- If the model cites an id that isn't an approved instruction it was given, the app shows "Ask your lead" instead.
- Safety notes are shown exactly as written in the approved instruction. If the model paraphrases one, the app swaps in the original text.
- Every question is logged (answered, source, helpful, time), and unanswered ones go to the supervisor's gaps list.

Model: `claude-opus-5-5` at low effort, with structured JSON output validated by pydantic. On a safety decline, the API retries on a fallback model in the same call (`fallbacks: "default"`). The API key is read from `.env` and never displayed.
