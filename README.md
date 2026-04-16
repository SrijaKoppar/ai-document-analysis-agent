# Document Analysis Agent

An intelligent, LLM-powered document analysis system that goes beyond simple text extraction.  
The system follows an **agentic pipeline**, where an orchestrator coordinates classification, planning, execution, and verification to extract structured insights from documents.

---

## Core Features

### 1. Intelligent Document Classification
- The agent first classifies the document type (e.g., Report, Questionnaire, Spreadsheet, Form).
- This enables **context-aware processing** instead of treating all documents the same.

---

### 2. Skill Registry Architecture
- Built using a modular **Skill Registry**.
- Skills (e.g., `extract_questions`, `summarize`) are dynamically selected by an LLM-based planner.
- New skills can be added easily without modifying the core system.

---

### 3. Structured Spreadsheet Analysis
- Supports Excel and CSV files.
- Extracts:
  - Sheet data
  - Column types
  - Basic statistics (min, max, mean)
- Enables structured understanding of tabular data.

---

### 4. Chunk-Based Summarization for Long Documents
- Handles large documents by splitting them into smaller chunks.
- Each chunk is summarized, and results are combined into a final summary.
- Helps overcome LLM context limitations.

---

### 5. Structured Question & Form Extraction
- Extracts questions and form fields into structured JSON.
- Captures:
  - Question types (MCQ, descriptive, yes/no)
  - Sections
  - Field labels
- Makes outputs usable for downstream systems.

---

## Key Design Principles

- **Modularity:** Each capability is implemented as an independent skill  
- **Dynamic Planning:** LLM decides execution flow instead of hardcoded rules  
- **Structured Outputs:** Results are returned as JSON for downstream use  
- **Local Execution:** Runs entirely on-device using Ollama for privacy  

---

## System Architecture

### Pipeline Flow

```mermaid
graph TD
    A[User Uploads Document] --> B[Ingestion Layer]
    B --> C{File Type?}
    C -- PDF --> D[Text Extraction]
    C -- Excel/CSV --> E[Spreadsheet Parser]
    D --> F[Classifier]
    E --> F
    F --> G[Planner]
    G --> H[Executor]
    H --> I[Skills]
    I --> J[Verifier]
    J --> K[Structured JSON Output]
