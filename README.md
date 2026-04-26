# TalentScout AI v4
### AI-Powered Recruitment Automation Platform

TalentScout AI is a fully local, browser-based recruitment agent that parses job descriptions, discovers and scores candidates, simulates realistic recruiter-candidate conversations, and produces a ranked shortlist — all running on your own machine with zero external API costs.

---

## What It Does

1. **Parse JD** — Paste any job description. The agent auto-extracts role title, required skills, preferred skills, and experience range.
2. **Discover Candidates** — Either scan the built-in database of 240 profiles across 24 roles, or upload your own PDF/DOCX CVs.
3. **Score & Match** — Every candidate is scored against the JD across three dimensions: Required Skills (60%), Preferred Skills (20%), Experience fit (20%).
4. **Engage** — Live chat with individual candidates (clickable suggestions, typing indicator, real-time Interest Score), or Auto-Engage all in parallel.
5. **Shortlist** — Ranked table combining Match Score (60%) and Interest Score (40%) into a Combined Score. Export to CSV.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+ · Flask 3.x |
| PDF Parsing | pdfplumber (text PDFs) · pytesseract + pdf2image (scanned/image PDFs) |
| DOCX Parsing | python-docx |
| Frontend | Vanilla HTML/CSS/JavaScript (no framework) |
| Data | In-memory (no database required) |
| Deployment | Local · localhost:5001 |

---

## Folder Structure

```
talentscout/
├── app.py                        # Flask backend — all routes and logic
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── parsed_candidates.csv         # Auto-generated after each CV upload session
├── uploads/                      # Temp folder — uploaded CVs are deleted after parsing
├── static/
│   ├── css/
│   │   └── style.css             # All UI styles
│   └── js/
│       └── app.js                # All frontend logic
└── templates/
    └── index.html                # Single-page app template
```

---

## Prerequisites

### 1. Python 3.10 or higher
Check your version:
```bash
python --version
```
Download from https://www.python.org/downloads/ if needed.

### 2. pip (Python package manager)
Usually comes with Python. Check:
```bash
pip --version
```

### 3. Tesseract OCR Engine (only needed for scanned/image PDFs)
This is a separate system-level install — **not a pip package**.

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (default path: `C:\Program Files\Tesseract-OCR\`)
3. Add to PATH: System Properties → Environment Variables → add `C:\Program Files\Tesseract-OCR` to PATH
4. Verify: open a new terminal and run `tesseract --version`

**macOS:**
```bash
brew install tesseract
```
(Install Homebrew first from https://brew.sh if needed)

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install poppler-utils
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install tesseract poppler-utils
```

> **Note:** If you only upload text-based PDFs (created from Word/Google Docs), Tesseract is optional. It is only required for scanned/photographed PDFs.

---

## Installation

### Step 1 — Clone or extract the project
If you have a ZIP file, extract it to a folder of your choice.

### Step 2 — Create a virtual environment (recommended)
```bash
cd talentscout
python -m venv venv
```
Activate it:
- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

### Step 3 — Install Python dependencies
```bash
pip install -r requirements.txt
```

This installs:
| Package | Purpose |
|---|---|
| flask | Web framework — runs the local server |
| pdfplumber | Extracts text from text-based PDFs |
| python-docx | Extracts text from DOCX files |
| pytesseract | Python wrapper for Tesseract OCR (scanned PDFs) |
| pdf2image | Converts PDF pages to images for OCR |
| pillow | Image processing library (required by pdf2image) |

### Step 4 — Run the app
```bash
python app.py
```

You should see:
```
  TalentScout AI v4 -> http://localhost:5001
```

Open your browser and go to: **http://localhost:5001**

---

## How to Use

### Mode A — Sample Database
1. Paste or load a sample JD → click **Parse Job Description**
2. Select **Sample Database** tab → click **Discover from Sample Database**
3. 6 top-matched candidates appear with skill scores
4. Either click **Chat Now** on any card for live conversation, or click **Auto-Engage All**
5. View engagement results → ranked shortlist → export CSV

### Mode B — Upload Your Own CVs
1. Paste or load a JD → click **Parse Job Description**
2. Select **Upload Your CVs** tab
3. Drag & drop or click to upload PDF or DOCX files (multiple at once)
4. Click **Parse CVs & Extract Candidate Info** — watch real-time progress
5. After parsing, click **Score & Match Against JD** — this runs the same full funnel as Mode A
6. Chat Now, Auto-Engage, Shortlist, Export CSV — all identical to Mode A
7. A `parsed_candidates.csv` file is auto-saved in your project folder with all extracted skills

---

## Supported CV Formats

| Format | Support | Notes |
|---|---|---|
| PDF (text-based) | Full | Created from Word, Google Docs, Adobe — text is selectable |
| PDF (scanned/image) | Full (with Tesseract) | Photographed or printed-then-scanned CVs — requires Tesseract OCR |
| DOCX | Full | Microsoft Word format |
| DOC | Partial | Older Word format — convert to DOCX for best results |

**How to tell if your PDF is text-based or scanned:**
Open the PDF and try to select/highlight text with your mouse. If you can select text → text-based. If you cannot → scanned, needs Tesseract.

---

## Built-in Candidate Database

240 candidates across 24 roles:

| Role Category | Roles Included |
|---|---|
| Data & Engineering | Data Engineer, Senior Data Engineer, Data Analyst, Data Operations Manager, Software Engineer |
| Revenue Operations | RevOps Manager, RevOps Analyst, Sales Operations Specialist, HubSpot Specialist, CRM Administrator, Zoho CRM Specialist |
| Marketing | Marketing Operations Manager, Marketing Operations Analyst |
| People & HR | HR Manager, HRBP, Talent Acquisition Specialist, Recruiter |
| Sales | SDR, Account Executive, Customer Success Manager, Customer Success Lead |
| Finance & Strategy | Finance Analyst, Business Analyst, Product Manager |

---

## Scoring Formula

**Match Score** (0–100):
- Required Skills matched: up to 60 points
- Preferred Skills matched: up to 20 points
- Experience fit: up to 20 points

**Combined Score** (final ranking):
```
Combined = Match Score × 60% + Interest Score × 40%
```

**Interest Score** is derived from candidate reply sentiment during conversation (positive signals like "open to", "let us connect", "available" increase it; negative signals decrease it).

---

## Troubleshooting

**"Could not extract text" on all PDFs**
→ Your PDFs are scanned. Install Tesseract OCR (see Prerequisites section above).

**Tesseract not found error**
→ Tesseract is installed but not in PATH. On Windows, add `C:\Program Files\Tesseract-OCR` to your system PATH and restart the terminal.

**pdf2image error on Windows**
→ Install poppler for Windows: https://github.com/oschwartz10612/poppler-windows/releases
→ Extract and add the `bin/` folder to your system PATH.

**Import "pdfplumber" could not be resolved (VS Code yellow warning)**
→ This is a Pylance/editor warning only. Press `Ctrl+Shift+P` → "Python: Select Interpreter" → choose the Python where you ran `pip install`. The app will still run fine regardless.

**Port already in use**
→ Change the port in the last line of `app.py`: `app.run(debug=True, port=5002)`

**Candidates all showing the same name after upload**
→ Make sure your PDFs have the person's name as readable text in the first 10 lines of the document.

---

## Notes

- All data is stored **in memory only** — restarting the server clears sessions
- Uploaded CV files are **automatically deleted** from the `uploads/` folder after parsing
- The `parsed_candidates.csv` is overwritten on each new upload session — rename it if you want to keep previous results
- No internet connection required after initial setup
- No API keys or external services required
