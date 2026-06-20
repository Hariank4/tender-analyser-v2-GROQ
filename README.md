# Tender Analyser v2 — Groq Edition

AI-powered government tender analysis tool. Upload any tender PDF — AI reads it, extracts all fields, checks organisational eligibility, scores bid strength, and generates ready-to-download Word documents.

Built with **Groq AI** (Llama 3.3 70B) for fast, free inference.

## Features

- **PDF Upload** — drag-and-drop or file browse
- **AI Field Extraction** — bid number, dates, fees, scope, eligibility, and 15+ more fields extracted automatically
- **Editable Preview** — correct any field before downloading
- **Tender One Pager (TOP.docx)** — formatted in exact organisational template with auto-incrementing reference numbers
- **Bid Intelligence Report (Report.docx)** — 8-section document with overview, scope, match analysis, and score
- **Match Engine** — checks 9 eligibility criteria against organisational profile (PMGDISHA, JJM, Lakhpati Didi, NDLM, PMAY-G, ISO, MSME, Geographic Reach, Beneficiary Scale)
- **Bid Strength Score** — AI-generated score out of 100 with win probability percentage
- **Gap Fixer** — for each unmatched criterion, AI explains why the gap exists, suggests framing strategy, what to write, and documents to reference
- **Sidebar Gap Reasons** — auto-loaded explanations under each ❌ criterion
- **Error Handling** — clear screens for rate limits, bad PDFs, and server issues

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.14, FastAPI, Uvicorn |
| AI | Groq API — `llama-3.3-70b-versatile` (free tier) |
| PDF Reading | PyMuPDF (fitz) |
| DOCX Generation | python-docx |
| Frontend | HTML, CSS, JavaScript (vanilla) |
| File Upload | python-multipart |

## Setup

```bash
# Clone the repo
git clone https://github.com/Hariank4/tender-analyser-v2-GROQ.git
cd tender-analyser-v2-GROQ

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn groq pymupdf python-docx python-dotenv python-multipart

# Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env
# Get a free key at https://console.groq.com

# Run the server
python3 main.py
# Open http://localhost:8001
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serve the frontend |
| `POST` | `/analyse` | Upload PDF → AI extracts all fields |
| `POST` | `/download/top` | Generate TOP.docx from extracted data |
| `POST` | `/download/report` | Generate Report.docx from extracted data |
| `POST` | `/gaps` | AI generates gap-fix strategies for unmatched criteria |

## Project Structure

```
tender-analyser-v2-GROQ/
├── .env                  ← GROQ_API_KEY (not committed)
├── .gitignore
├── README.md
├── main.py               ← FastAPI server, 5 endpoints
├── ai.py                 ← Groq API calls, analyse_tender(), fix_eligibility_gaps()
├── docx_generator.py     ← generate_top_docx(), generate_report_docx()
├── top_counter.txt       ← Auto-incrementing TOP reference counter
└── frontend/
    └── index.html        ← Full UI — upload, loading, results, gap modal
```

## Rate Limits

Groq free tier allows ~100K tokens/day for `llama-3.3-70b-versatile`. Each tender analysis uses ~3K–5K tokens. If you hit the limit, wait for the daily reset — the app will show a clear "⏳ Groq Rate Limit Hit" message.

## Author

**Hariank Juneja** — B.Tech CSE (Generative AI)