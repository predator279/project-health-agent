# Project Health Reporting Agent

This repository contains the codebase for the Project Health Reporting Agent, an AI-driven tool that automatically parses project plans, determines their RAG (Red/Amber/Green) status, and synthesizes the insights into an executive-level monthly presentation.

---

## 🚀 How to Run

### 1. Setup
Ensure you have Python 3.11+ installed. Clone this repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Generate Weekly Reports (Phase 2)
Run the agent against project plans to parse the schedules, score them against the RAG framework, and generate structured JSON and Markdown outputs.

```bash
python -m src.cli run-weekly --input "data/sample_inputs/S2P Project.xlsx" --out "data/outputs/weekly"
python -m src.cli run-weekly --input "data/sample_inputs/Project Plan B.xlsx" --out "data/outputs/weekly"
```
*(The outputs will be placed in `data/outputs/weekly/` categorized by project.)*

### 3. Generate Monthly Executive Deck (Phase 3)
Aggregate the weekly outputs to detect portfolio trends and generate a ready-to-present PowerPoint deck.

```bash
python -m src.cli run-monthly --inputs "data/outputs/weekly/S2P_Project/latest.json" "data/outputs/weekly/Project_Plan_B/latest.json" --out "data/outputs/monthly"
```
*(The presentation will be saved in `data/outputs/monthly/`.)*

---

## 🧠 Phase 1: RAG Methodology & Framework

The system is built on a robust, standardized framework to ensure it is auditable, testable, and resistant to hallucinations.

### 1. Canonical Data Schema (The Parser's Contract)
Whatever the source file format (Excel, Word, PDF), the parser's only job is to extract the raw data and populate a standardized intermediate schema (a Pydantic `ProjectPlan` object). 
* **Why**: Separating "reading the file" from "scoring the project" means a new file format only requires a new adapter, not new scoring logic.

### 2. RAG Scoring & Roll-up Logic
* **Worst-Of Rollup**: We aggregate statuses from Task -> Phase -> Project using a "worst-of" logic. If one critical phase is Red, the project flags Red.
  * **Why**: Worst-of avoids the common failure mode of averaging a real risk away among many green tasks. For client-facing reporting, under-stating risk is the worse error.
* **30% Override Trigger**: Even if no single phase triggers a Red, if >30% of all open tasks are overdue, the system escalates the project status to Red automatically. This catches broad, shallow drift.

### 3. Evidence & Reasoning Generation
Reasoning is produced in two strictly separated layers:
1. **Evidence Layer**: The scoring step outputs a structured record (e.g., `schedule -> Red -> "UAT Signoff overdue 14 days"`).
2. **Narrative Layer**: The plain-English write-up is composed *only* from evidence records. 
* **Why**: Grounding the narrative strictly in the evidence object is the ultimate **anti-hallucination guardrail**. Even if an LLM is used to smooth the phrasing, it cannot introduce a fact, date, or number that isn't explicitly in the evidence record.

### 4. Cross-Project Trends & Risks (Phase 3 Foundation)
* **Trend**: A trend is detected when the same signal type (e.g., "Schedule Slippage") triggers Amber or Red in 2 or more projects during the same reporting cycle. 
* **Emerging Risk**: Flagged when a project is Amber (or Green with an unresolved blocker) and its evidence trajectory is trending worse over time. (Note: Kept conservative here due to a single-week snapshot in the sample data).

---

## 🛠 Key Design Decisions

1. **Parser Adapters with Fuzzy Matching**: Instead of hardcoding Excel column indices, the `xlsx_adapter` uses fuzzy matching to map headers (e.g., dynamically handling the missing `Level` column in `Project Plan B.xlsx`).
2. **Graceful Degradation**: Extended signals like Budget Burn degrade gracefully. If the source file does not have budget/cost columns, the scoring engine returns `Not Scored` rather than failing or assuming the project is on budget.
3. **Data Confidence Tags**: Every parsed field is tagged (`direct`, `inferred`, `missing`). If >15% of fields are missing or inferred (as is common with unstructured PDFs), the `Data Confidence` drops to Medium or Low, explicitly alerting the VP on the executive deck so they don't treat inferred data with false uniform confidence.
4. **Zero LLM Cost / 100% Deterministic**: Because the `narrative_composer` synthesizes the text natively from structured evidence, the core pipeline for `.xlsx` files requires zero external LLM API calls, making it 100% free and incredibly fast.

## ⚙️ Configuration

All RAG thresholds (e.g., how many days late constitutes a "Red" vs "Amber" status, blocker keywords) are externalized in `config/rag_thresholds.yaml`. This allows project managers to recalibrate the sensitivities dynamically without needing an engineer to edit Python code.
