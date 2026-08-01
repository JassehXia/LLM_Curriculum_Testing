# Project Handoff: Autonomous LLM Curriculum Testing & Generation Pipeline

## 1. Project Vision & Goals

This project builds an **autonomous, self-healing deep learning curriculum generation pipeline** for university courses.

Given open-ended curriculum module descriptions (in `test.yaml`), the pipeline:

1. Generates structured learning materials (starter code, reference solutions, unit tests, slides) using **Instructor** and **Qwen 2.5 7B Instruct**.
2. Automatically validates all generated code in a **live PyTorch subprocess sandbox** (`sandbox.py`).
3. Executes a **self-healing retry loop** where runtime exceptions and unit test failures are fed back to the LLM to auto-correct PyTorch code errors before saving.
4. Exports verified student exercises, solutions, and tests to the `outputs/` directory.

---

## 2. Infrastructure & System Architecture

### A. NRP Nautilus Kubernetes GPU Server (`nautilus-pod.yaml`)

- **Cluster:** NRP Nautilus (National Research Platform Kubernetes Cluster).
- **Pod Manifest:** [nautilus-pod.yaml](file:///c:/Desktop/Coding%20Projects/LLM_Curriculum_Testing/nautilus-pod.yaml)
- **Model Hosted:** `Qwen/Qwen2.5-7B-Instruct` served via `vLLM` on port 8000.
- **Node Requirements:** `runtimeClassName: nvidia`, `nvidia.com/gpu: 1` (A100 80GB, L40S 48GB, or RTX A6000).
- **Port Forwarding:** `kubectl port-forward pod/curriculum-vllm-sandbox 8000:8000` tunnels the GPU server to `http://localhost:8000/v1` on your local machine.

### B. Core Code Base Structure

- **[test.yaml](file:///c:/Desktop/Coding%20Projects/LLM_Curriculum_Testing/test.yaml):** High-level curriculum specification listing modules (e.g. U-Net segmentation, Grad-CAM XAI).
- **[test_generator.py](file:///c:/Desktop/Coding%20Projects/LLM_Curriculum_Testing/test_generator.py):** Main driver script that iterates through modules, invokes Instructor structured completions, triggers sandbox validation, and writes outputs to `outputs/`.
- **[schemas/generation_types.py](file:///c:/Desktop/Coding%20Projects/LLM_Curriculum_Testing/schemas/generation_types.py):** Pydantic schemas (`ValidatedExerciseSchema`, `SlideDeckSchema`) featuring a `@model_validator(mode="after")` that runs `sandbox.py` automatically during validation.
- **[sandbox.py](file:///c:/Desktop/Coding%20Projects/LLM_Curriculum_Testing/sandbox.py):** Subprocess execution sandbox that runs combined `solution_code` + `unit_test` in the project's local virtual environment (`.venv`).
- **[context.py](file:///c:/Desktop/Coding%20Projects/LLM_Curriculum_Testing/context.py):** Domain-agnostic, open-ended system prompt builder (`build_system_prompt()`) enforcing self-contained Python code rules.
- **[ai_setup.py](file:///c:/Desktop/Coding%20Projects/LLM_Curriculum_Testing/ai_setup.py):** Instructor client factory wrapper.

---

## 3. Current Work & Verification Accomplished

- **Nautilus Pod Live & Verified:** Pod `curriculum-vllm-sandbox` is `1/1 Running` on Nautilus serving `Qwen/Qwen2.5-7B-Instruct`.
- **PyTorch Virtualenv Sandbox Fixed:** Installed `torch` and `numpy` into `.venv`. `sandbox.py` automatically detects and uses `.venv/Scripts/python.exe`.
- **Verified Attempt #1 Generation Success:** Successfully generated and verified `unet_segmentation` exercise assets on the first try with 0 retries required!
- **Git Repository State:** Clean, all updates committed and pushed to `main` branch on GitHub (`JassehXia/LLM_Curriculum_Testing`).

---

## 4. Key Open Challenges & Generalizable Generation Failures

### A. Generalizable LLM Failure Modes

1. **API Signature & Library Hallucinations:**
   - *Issue:* In open-ended prompts, LLMs occasionally invent non-existent parameters or import paths for specialized libraries (`torchvision`, `transformers`, `scikit-learn`).
   - *Mitigation:* Pydantic runtime schema validation combined with live Python subprocess execution in `sandbox.py`.

2. **File-System vs. In-Memory Scope Assumptions:**
   - *Issue:* LLMs are trained on multi-file repos, leading them to write unit tests with fictitious imports (`from solution_code import ...`) or local file reads (`open('dataset.csv')`).
   - *Mitigation:* `sandbox.py` sanitization and system prompt directives enforcing self-contained, in-memory execution.

3. **Tensor Arithmetic & Logic Drift (Cyclic Fix Loops):**
   - *Issue:* Complex architectural math (channel counts, spatial dimensions, matrix multiplications) can cause the LLM to get caught in cyclic fix loops where fixing step A breaks step B.
   - *Mitigation:* Self-healing retry loops (`max_retries=5-7`) with live stack traces fed back into Instructor.

4. **Exponential Prompt Context Inflation:**
   - *Issue:* Appending full stack traces and code iterations on every retry causes prompt size to grow linearly ($\sim O(N)$ growth per retry), eventually threatening context window limits.
   - *Mitigation:* Configured vLLM `--max-model-len=32768` (or `65536`) to grant ample context headroom for multi-turn history.

### B. Core Philosophy & Directives

- **Domain-Agnostic Generation:** Prompts must remain high-level and open-ended without hardcoded architectural templates or domain hints.
- **Pure Self-Healing Pipeline:** Rely on Python runtime tracebacks and Pydantic validation to guide LLM repair rather than pre-packaged code templates.

---

## 5. Next-Gen 3-Phase Pipeline & Context-Wiping Architecture

### A. The 3-Phase Generation Pipeline

To eliminate hallucinations and ground code generation in verified research without template hints, the pipeline is designed in 3 sequential phases per module:

```
[test.yaml] ──> Phase 1: Research Agent (saves research/{id}_notes.md)
                   └──> Phase 2: Slide Generator (saves outputs/{id}_slides.json)
                           └──> Phase 3: Exercise Generator (runs sandbox.py & saves code)
```

1. **Phase 1 (Research & Retrieval):**
   The LLM acts as a researcher, gathering official PyTorch documentation signatures, tensor dimension formulas, and mathematical explanations, saving them to `research/{module_id}_notes.md`.
2. **Phase 2 (Concept Teaching & Slide Synthesis):**
   The LLM reads `research/{module_id}_notes.md` and generates structured presentation slides (`SlideDeckSchema`), organizing concepts into bullet points and code snippets.
3. **Phase 3 (Grounded Exercise Generation):**
   The LLM generates `ValidatedExerciseSchema` (starter code, reference solution, unit test) grounded in the research notes and slide deck, executing live PyTorch verification in `sandbox.py`.

### B. Stateless Context Wiping Between Modules

- **Context Reset Mechanism:** API completion calls (`client.chat.completions.create`) are stateless by default.
- When Module 1 completes and the loop moves to Module 2, passing a fresh `messages` payload resets the prompt context window to **0 tokens automatically**.
- No prompt history or error tracebacks leak from one module to the next!

---

## 6. Recommended Next Steps for Incoming Agent

1. **Implement 3-Phase Pipeline:** Update `test_generator.py` to execute Phase 1 (Research) $\rightarrow$ Phase 2 (Slides) $\rightarrow$ Phase 3 (Exercises).
2. **Context Length Expansion:** Update [nautilus-pod.yaml](file:///c:/Desktop/Coding%20Projects/LLM_Curriculum_Testing/nautilus-pod.yaml) `--max-model-len` to `32768` for ample context headroom during retries.
3. **Batch Multi-Module Execution:** Test the 3-phase pipeline across all modules in `test.yaml` (`unet_segmentation`, `gradcam_xai`).

---

## 7. Quick Start Commands

```powershell
# 1. Port Forward Nautilus GPU pod to local machine
kubectl port-forward pod/curriculum-vllm-sandbox 8000:8000

# 2. In a 2nd terminal window, execute generator
.venv\Scripts\python.exe test_generator.py
```
