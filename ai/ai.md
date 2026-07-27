# Repository Objective: Standalone LLM Content Generator Testbed

You are an expert AI engineer assisting in building a lightweight, isolated sandbox repository (`curriculum-llm-sandbox`). This repository prototypes on-the-fly educational content generation using a locally served Qwen 2.5 LLM, Instructor, and `python-pptx` before integrating it into a larger curriculum generator pipeline.

---

## Technical Stack & Infrastructure

- **LLM Engine:** `Qwen/Qwen2.5-3B-Instruct` (or `32B-Instruct`) hosted locally on an OSC (Ohio Supercomputer Center) GPU compute node using **vLLM** (exposing an OpenAI-compatible HTTP API at `http://localhost:8000/v1`).
- **Structured Validation:** `instructor` + `pydantic` v2.
- **Self-Healing Code Execution Loop:** Pydantic `@field_validator` executing generated PyTorch solutions against generated unit tests in a temporary `subprocess` sandbox. Failing tests raise `ValueError(error_log)` to trigger Instructor's automatic retry logic (`max_retries=3`).
- **Presentation Engine:** `python-pptx` (headless presentation builder reading validated Pydantic JSON schemas).
- **User Input:** Lightweight `config.yaml` specifying simple pedagogical directives (`id`, `title`, `week`, `context`, `exercise`).

---

## Core File Responsibilities

1. `config.yaml`: Minimal YAML input where educators specify modules and lightweight directives.
2. `schemas.py`: Pydantic v2 schemas (`SlideDeckSchema`, `ValidatedExerciseSchema`). `ValidatedExerciseSchema` contains the `@field_validator` that runs solution code against unit tests in a subprocess.
3. `context.py`: Utility functions that parse optional pipeline metric JSONs (like 5-fold cross-validation accuracy) and format enriched prompts for Qwen.
4. `slide_builder.py`: Ingests `SlideDeckSchema` objects and uses `python-pptx` to construct and save `.pptx` files.
5. `test_generator.py`: Main entry point that loads config, calls Instructor, executes the self-healing validation loop, and saves output assets.

---

## Architectural Rules for Code Generation

- **Zero Cloud APIs:** All calls must target the local vLLM endpoint (`base_url="http://localhost:8000/v1"`, `api_key="none"`).
- **Type Safety First:** Never parse raw JSON strings manually using `json.loads()`. Use Instructor and Pydantic models to guarantee type safety.
- **Headless Execution:** Avoid dependencies that require a desktop GUI or Microsoft Office installation. `python-pptx` and `subprocess` must run natively on Linux compute nodes.
- **Clean Subprocess Sandboxing:** Always write temporary test scripts using `tempfile.NamedTemporaryFile` and ensure cleanup in `finally` blocks. Capture both stdout and stderr for detailed error tracebacks during Instructor retries.
