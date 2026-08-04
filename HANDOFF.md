# Autonomous LLM Curriculum Generation Pipeline - System Documentation & Handoff

## 1. Overview & System Vision

This system is an **Autonomous Telemetry-Driven LLM Curriculum Generation Pipeline**. It converts high-level educator directives (`test.yaml`) and Phase 1 machine learning training telemetry (`first_phase_outputs/`) into complete, domain-grounded teaching suites.

For every curriculum module, the pipeline autonomously synthesizes:

1. **Student Concept & Domain Overview Document** (`.md`)
2. **Widescreen Presentation Slide Deck** (`.pptx`)
3. **Student Starter Skeleton Code** (`.py`)
4. **Verified PyTorch Reference Solution** (`.py`)
5. **Standalone Property-Based Unit Tests** (`.py`)
6. **Structured Metadata Payload** (`.json`)

---

## 2. Infrastructure & System Stack

* **LLM Serving Engine:** `Qwen/Qwen2.5-Coder-14B-Instruct-AWQ` served via `vLLM` on NRP Kubernetes cluster (`sailab` namespace) with a **32,768 token context window**.
* **Structured Generation Framework:** **Instructor** wrapping OpenAI-compatible `/v1/chat/completions` for strict Pydantic v2 schema enforcement.
* **3-Stage Agent Architecture:**
  * **Agent 0 (Curriculum Director & Problem Formulation Agent)**: Ingests Phase 1 telemetry, extracts statistical contrastive samples, formulates domain shape contracts, and synthesizes Markdown overview documents (`.md`).
  * **Agent 1 (Code Generator Agent)**: Generates student starter code and reference PyTorch solutions.
  * **Agent 2 (Adversarial QA Agent)**: Synthesizes property-based unit test suites and validates execution in the sandbox.
* **Self-Healing Execution Sandbox:** Subprocess execution environment running inside the project `.venv` (`sandbox.py`). If unit test verification fails, runtime tracebacks are fed back to the LLM for automated iterative repair.
* **Presentation Engine:** **`python-pptx`** for programmatic 16:9 widescreen PowerPoint deck creation (`slide_builder.py`).
* **Local RAG Vector Store:** **ChromaDB** persistent vector index (`./chroma_db`) containing 5,290 embedded text and PyTorch code chunks from `rasbt/deeplearning-models` via `all-MiniLM-L6-v2`.

---

## 3. Telemetry Ingestion & Domain-Agnostic Sampling

The system ingests real dataset metrics and execution logs from Phase 1 (`first_phase_outputs/`):

* `run_summary.json`: Overall accuracy, AUC-ROC, class balance, and specific error counts (e.g. false negatives).
* `cv_report.json`: 5-fold cross-validation performance metrics.
* `class_mapping.json`: Domain class labels (e.g., `{"0": "benign", "1": "malignant"}`).
* `results.csv`: Per-sample prediction metrics, probabilities, SAM masks, and Grad-CAM map paths.

### Universal 4-Sample Contrastive Matrix

To remain 100% domain-agnostic across Vision, NLP, Audio, and Tabular tasks, `core/telemetry.py` extracts 4 representative data points using universal statistical rules:

1. **`[TOP_SUCCESS]`**: High-confidence correct prediction ($P \ge 0.99$).
2. **`[HARD_FAILURE]`**: High-confidence misclassifications (e.g., False Negatives).
3. **`[BOUNDARY_UNCERTAINTY]`**: Samples nearest the 50/50 decision boundary.
4. **`[MINORITY_SAMPLE]`**: Representative instance from the least frequent class.

---

## 4. 3-Stage Agent Architecture & Execution Flow

```
[ Phase 1 Telemetry ] ──> [ Agent 0: Problem Formulation ] ──> [ Agent 1: Code Generator ] ──> [ Agent 2: QA Sandbox Agent ]
 (run_summary, csv,       - Analyzes 4 contrastive samples     - Synthesizes PyTorch solution   - Writes property tests
  class_mapping)          - Formulates shape contracts         - Builds student starter code    - Runs .venv sandbox check
                          - Outputs {module}_overview.md       - Aligns with Agent 0 problem    - Triggers self-healing retries
```

### Final Output Suite per Module (`outputs/`)

```
outputs/
├── {id}_overview.md             # Student Markdown concept & domain overview
├── {id}_presentation.pptx       # Native 16:9 widescreen PowerPoint slide deck
├── {id}_slides.json             # Slide deck JSON schema
├── {id}_exercise.py             # Student starter skeleton code with TODOs
├── {id}_solution.py             # Verified reference PyTorch solution
├── {id}_test.py                 # Standalone PyTorch unit test harness
└── {id}_generated.json          # Complete module metadata payload
```

---

## 5. Addressed Architectural Concerns & Roadmap

### A. Pseudo-Code & Uninitialized Boilerplate (`DataLoader(...)`, `DEVICE`)

* **Observation**: Base Qwen occasionally outputs tutorial-style boilerplate (`DataLoader(...)`, `features.to(DEVICE)`) from its base pretraining corpus.
* **Mitigation**: Added strict system prompt guardrails forbidding placeholder ellipses `...` and requiring self-contained module definitions.

### B. QLoRA Fine-Tuning Recommendation for Qwen 14B

* **Recommendation**: Fine-tune `Qwen2.5-Coder-14B` using **QLoRA** on ~150 curated clean PyTorch solution pairs.
* **vLLM Multi-LoRA Serving**: vLLM natively supports Multi-LoRA serving (`--enable-lora`). You can run Agent 0, Agent 1, and Agent 2 adapters simultaneously on the same base 14B vLLM instance with **zero extra GPU memory cost**.

### C. Conceptual Verification vs. Full Dataset Loops

* The execution sandbox intentionally tests **architectural contracts, shape invariants, custom loss functions, and hook mechanisms** using in-memory synthetic tensors.
* Disk DataLoaders and multi-epoch convergence training are omitted from sandbox execution to maintain 100% deterministic, instant verification within the 120-second timeout.
