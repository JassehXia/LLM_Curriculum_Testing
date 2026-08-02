# Autonomous LLM Curriculum Generation Pipeline - System Documentation

## 1. Overview & Vision

For this iteration, the pipeline moves from **templated practice** to a **complete text-based, LLM content-generated curriculum**. Given high-level educator directives in a YAML configuration file, the system autonomously synthesizes grounded presentation slides, PyTorch exercise skeletons, reference solutions, and unit tests.

---

## 2. System Setup & Tech Stack

The key to reliable generation is a **constrained setup for deterministic output**, while ensuring outputs are **verified and tested on the fly**:

* **LLM Engine:** `Qwen/Qwen2.5-7B-Instruct` served via `vLLM` / **Tapis FlexServ** on GPU infrastructure.
* **Structured Input/Output:** **Instructor** library wrapping OpenAI API specs for strict Pydantic v2 schema enforcement.
* **Self-Healing Error Correction:** Automated retry loops where runtime exceptions and unit test failures are caught and appended back into the prompt for iterative LLM auto-repair.
* **Presentation Engine:** **`python-pptx`** for programmatic 16:9 widescreen PowerPoint slide deck generation.
* **Local RAG Vector Store:** **ChromaDB** persistent vector index (`./chroma_db`) holding 5,290 embedded text and PyTorch code chunks from `rasbt/deeplearning-models` via `all-MiniLM-L6-v2`.

---

## 3. User Configuration (`test.yaml`)

Educators simply add or modify their curriculum modules in the input YAML configuration file:

```yaml
curriculum:
  subject: "Applied Deep Learning in Medical Imaging"
  target_level: "Undergraduate / Sophomore"
  
  modules:
    - id: "unet_segmentation"
      title: "U-Net Architecture & Skip Connections"
      week: 3
      context: "Focus on why skip connections prevent spatial information loss during upsampling. Relate to skin lesion boundary segmentation."
      difficulty: "Intermediate"

    - id: "gradcam_xai"
      title: "Explainable AI with Grad-CAM"
      week: 5
      context: "Explain visual feature attribution and hook registration on PyTorch ViT/CNN blocks."
      difficulty: "Advanced"
```

### YAML Configuration Fields

* `id`: Unique string identifier for the module (used in output filenames).
* `title`: Full human-readable title of the curriculum module.
* `week`: Target course week in which the module resides.
* `context`: Specific directives provided by the educator detailing what concepts to emphasize.
* `difficulty`: Difficulty level (`Basic`, `Intermediate`, `Advanced`) used for calibration.

---

## 4. System Execution Flow

```
1. GPU Endpoint Setup ──> 2. Educator YAML Input ──> 3. RAG Retrieval Engine ──> 4. Qwen Generation & Sandbox Verification
   - vLLM / FlexServ         - Module title, week        - ChromaDB (./chroma_db)      - Step A: Slide Deck (.pptx)
   - OpenAI API Spec         - Directives & Context      - Top 2-3 Snippets (< 5ms)     - Step B: Sandbox Retry Loop
```

### A. Infrastructure Setup

Set up vLLM / Tapis FlexServ to expose an OpenAI-compliant REST endpoint returning structured JSON payloads (`/v1/chat/completions`).

### B. Educator Input & Prompt Expansion

`test_generator.py` ingests module specifications from `test.yaml`, combining them with system rules enforcing Bloom's Taxonomy, ABET learning outcomes, and self-contained PyTorch script rules.

### C. Local RAG Research & Retrieval Phase

Instead of web scraping, the system queries a local persistent **ChromaDB** index (`./chroma_db`):

* Pulls official documentation snippets, conceptual explanations, and verified PyTorch code structures from [rasbt/deeplearning-models](https://github.com/rasbt/deeplearning-models).
* Injects top 2-3 matching snippets ($\sim 1,000$ tokens) into the prompt context, leaving 95%+ of Qwen's 32,768 context window free.

### D. Qwen 3-Step Generation & Verification

1. **Research Grounding:** Pulls local vector embeddings from ChromaDB for topic context.
2. **Slide Deck Generation:** Uses `python-pptx` and `SlideDeckSchema` to synthesize widescreen PowerPoint presentation decks (`presentation.pptx`).
3. **Sandbox Verification & Self-Healing:** Uses Instructor to run live PyTorch code execution inside a `.venv` subprocess (`sandbox.py`). If unit tests fail, the error log is fed back to Qwen for auto-correction before saving.

---

## 5. Verification & Self-Healing Sandbox Loop

```
┌──────────────────────────┐
│  Qwen Generates JSON     │ (solution_code + unit_test)
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Pydantic Field Validator│ (@model_validator mode="after")
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Live Subprocess Execution│ (sandbox.py inside .venv)
└────────────┬─────────────┘
             │
       ┌─────┴─────────────────────────────────┐
       │                                       │
       ▼                                       ▼
 [Tests Pass]                             [Tests Fail]
  Return validated object                  Raise ValueError with trace log
  Proceed to file export                   Instructor appends error to prompt
                                           Qwen retries generation (up to 7x)
```

1. **Generation:** Qwen generates `solution_code` and `unit_test` inside `ValidatedExerciseSchema`.
2. **Validation:** Pydantic triggers `@model_validator` which passes the code directly to `sandbox.py`.
3. **Execution:** A subprocess executes `solution_code` + `unit_test` cleanly inside the project's `.venv`.
4. **Verification Outcome:**
   * **If Tests Pass:** The process returns the validated object and exports files to `outputs/`.
   * **If Tests Fail:** `sandbox.py` captures the exact Python stack trace; Instructor catches the error, appends it to the prompt history, and Qwen retries auto-repair (up to 7 iterations).

---

## 6. Final Output Structure (`outputs/`)

Each module generates an isolated set of verified teaching assets:

```
outputs/
├── {id}_presentation.pptx       # Native widescreen PowerPoint slide deck
├── {id}_slides.json             # Structured slide deck schema JSON
├── {id}_exercise.py             # Student starter skeleton code with TODOs
├── {id}_solution.py             # Verified reference PyTorch solution
├── {id}_test.py                 # Standalone PyTorch unit test suite
└── {id}_generated.json          # Full metadata payload
```
