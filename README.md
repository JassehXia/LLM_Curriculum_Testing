# LLM Curriculum Content Generator Testbed

A standalone sandbox for prototyping on-the-fly educational curriculum content generation using locally served **Qwen 2.5**, **Instructor**, and **python-pptx**.

## Overview

This repository isolates and tests the module generation pipeline for the main curriculum generation project. It processes pedagogical directives specified in a YAML configuration, executes a self-healing verification loop using Pydantic validators and subprocess test execution, and generates presentation slide decks (`.pptx`) and PyTorch exercise files (`.py`).

## Technical Stack

- **LLM Engine:** Local `Qwen/Qwen2.5-3B-Instruct` (or `32B-Instruct`) hosted via **vLLM** (OpenAI-compatible HTTP API endpoint at `http://localhost:8000/v1`).
- **Structured Validation:** `instructor` + `pydantic` v2.
- **Self-Healing Loop:** Pydantic `@field_validator` running generated solution code against unit tests in a `subprocess` sandbox with auto-retries via Instructor (`max_retries=3`).
- **Presentation Engine:** `python-pptx` (headless presentation slide builder).
- **Configuration:** YAML directive files (`config.yaml`).

## Project Structure

```
.
├── ai/
│   ├── ai.md               # Technical architecture & repo directives
│   └── outline.md          # Curriculum workflow & schema specs
├── .env.example            # Environment configuration template
├── .gitignore              # Standard git ignore rules
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

## Setup Instructions

1. **Create Virtual Environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate Virtual Environment:**
   - **Windows:** `.venv\Scripts\activate`
   - **Linux/macOS:** `source .venv/bin/activate`

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
