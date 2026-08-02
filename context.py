import os
import logging
# Limit CPU thread usage for PyTorch / SentenceTransformers to prevent 100% CPU spikes
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

try:
    import torch
    torch.set_num_threads(2)
except Exception:
    pass

import chromadb
from typing import Dict, Any, Optional, cast
from chromadb.utils import embedding_functions
from schemas import Module, ValidatedExerciseSchema, SlideDeckSchema

# Local Persistent Database Directory
DB_DIR = "./chroma_db"

# Cached collection instance to prevent re-instantiating model weights on every query
_cached_collection = None

def _get_collection():
    global _cached_collection
    if _cached_collection is None and os.path.exists(DB_DIR):
        try:
            client = chromadb.PersistentClient(path=DB_DIR)
            ef = cast(
                Any,
                embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            )
            _cached_collection = client.get_collection(
                name="rasbt_models_rag",
                embedding_function=ef
            )
        except Exception as e:
            print(f"Warning: Failed to load ChromaDB collection: {e}")
            _cached_collection = None
    return _cached_collection

def get_rag_context(query_text: str, n_results: int = 2, chunk_type: Optional[str] = None) -> str:
    """
    Queries local ChromaDB vector store for top matching context snippets.
    """
    collection = _get_collection()
    if collection is None:
        return ""

    try:
        where_clause = {"type": chunk_type} if chunk_type else None
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=cast(Any, where_clause)
        )

        docs_list = results.get("documents")
        metas_list = results.get("metadatas")

        if not docs_list or not docs_list[0]:
            return ""

        docs = docs_list[0]
        metas = metas_list[0] if metas_list else []
        formatted_snippets = []

        for doc, meta in zip(docs, metas):
            source_file = meta.get("file", "unknown")
            snippet_type = meta.get("type", "snippet")
            formatted_snippets.append(
                f"[Reference: {source_file} | Type: {snippet_type}]\n{doc}"
            )

        return "\n\n".join(formatted_snippets)

    except Exception as e:
        print(f"Warning: RAG retrieval failed: {e}")
        return ""

def build_system_prompt() -> str:
    return (
        "You are an expert deep learning educator.\n"
        "Generate curriculum content following Bloom's Taxonomy and ABET outcomes.\n"
        "CRITICAL CODE RULES:\n"
        "1. Every `solution_code` and `unit_test` string MUST be a fully self-contained, valid Python script.\n"
        "2. ALWAYS include all necessary module imports at the very top of `solution_code` and `unit_test` (e.g., `import torch`, `import torch.nn as nn`, `import torch.nn.functional as F`).\n"
        "3. All generated PyTorch code must execute cleanly without SyntaxError, NameError, or AttributeError.\n"
        "4. In `unit_test`, test the classes/functions defined in `solution_code` directly in memory. NEVER use placeholder imports (e.g. `from your_module import ...`) or load non-existent files (`torch.load('path...')`).\n"
        "5. In `unit_test`, pass a dummy tensor into the model and assert that the output tensor shape matches expectation.\n"
        "6. ONLY use standard PyTorch / torchvision model names (e.g., `resnet18`, `resnet50`, `vit_b_16`, `convnext_tiny`). DO NOT invent non-existent model names like `vit_base_patch16_224`.\n"
        "7. NEVER attempt to open or load non-existent image or data files from disk (e.g., `Image.open('path_to_image.jpg')`, `cv2.imread()`). ALWAYS create synthetic in-memory dummy tensors (e.g., `torch.randn(1, 3, 224, 224)`) for image and data inputs.\n"
        "8. Pay careful attention to tensor dimensions: if `image_tensor` is already a 4D tensor `[N, C, H, W]`, DO NOT call `unsqueeze(0)` on it. Ensure all `conv2d` inputs remain 4D.\n"
    )

def build_slide_prompt(module: Module) -> str:
    query = f"{module.title} {module.context}"
    rag_context = get_rag_context(query, n_results=2, chunk_type="explanation")

    prompt = (
        f"Generate presentation slides for module '{module.title}' (Week {module.week}).\n"
        f"Context: {module.context}\n"
        f"Difficulty: {module.difficulty}\n"
    )
    if rag_context:
        prompt += f"\n--- GROUNDED REFERENCE CONTEXT ---\n{rag_context}\n"

    prompt += (
        "\nCreate a slide deck with a title slide and 3-5 content slides. "
        "Each content slide must contain 3-4 bullet points explaining concepts and optional PyTorch code snippets."
    )
    return prompt

def build_exercise_prompt(module: Module, slide_deck: Optional[SlideDeckSchema] = None, metrics: Optional[Dict[str, Any]] = None) -> str:
    query = f"{module.title} {module.context}"
    rag_context = get_rag_context(query, n_results=2, chunk_type="code")

    prompt = (
        f"Generate a PyTorch exercise for module '{module.title}' (Week {module.week}).\n"
        f"Context: {module.context}\n"
        f"Difficulty: {module.difficulty}\n"
    )
    if rag_context:
        prompt += f"\n--- GROUNDED PYTORCH CODE TEMPLATES ---\n{rag_context}\n"
    if slide_deck:
        prompt += f"\n--- SLIDE DECK TOPICS ---\nTitle: {slide_deck.deck_title}\nSlides: {[s.title for s in slide_deck.slides]}\n"
    if metrics:
        prompt += f"\nPipeline Artifact Metrics:\n{metrics}\n"
    return prompt
