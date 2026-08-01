# Tapis FlexServ API Endpoint Reference & Payload Documentation

This document provides a comprehensive reference for all REST API endpoints supported by **Tapis FlexServ**, including authentication headers, request payload formats, response schemas, and cURL / Python examples.

---

## 1. Authentication & Base Configuration

All requests sent to FlexServ require SSL warning bypass (if using custom/self-signed HPC cluster ports) and authentication tokens.

* **Base URL:** `https://stampede3.tacc.utexas.edu:60055/v1`
* **Default Token:** `flexserv`

### Required HTTP Headers

```http
Authorization: Bearer flexserv
x-flexserv-token: flexserv
Content-Type: application/json
```

---

## 2. Supported Endpoint Summary

| Endpoint Route | Method | Description | Primary Use Case |
| :--- | :---: | :--- | :--- |
| `/v1/models` | `GET` | Lists available loaded models & engines | Discover active model IDs |
| `/v1/chat/completions` | `POST` | OpenAI-compatible multi-turn chat completions | Text LLMs, Instructor JSON schemas, Slide/Code generation |
| `/v1/completions` | `POST` | Raw text generation & prompt completions | Single-prompt text continuation |
| `/v1/responses` | `POST` | Structured response generation | Formatted response schemas |
| `/v1/embeddings` | `POST` | Generates vector embeddings for input text | RAG vector indexing & semantic search |
| `/v1/audio/transcriptions` | `POST` | Transcribes audio files via Whisper models | Audio-to-text processing |
| `/v1/vision` / `/v1/yolo` | `POST` | Vision model inference & bounding box detection | Multimodal image feature extraction |
| `/v1/pipeline` | `POST` | Executes custom multi-stage inference pipelines | Custom AI workflows |
| `/metrics` | `GET` | Returns GPU memory & throughput telemetry | Monitoring server performance |

---

## 3. Detailed Endpoint Schemas & Payload Request Formats

### A. List Models API (`GET /v1/models`)

Returns all currently served models (e.g. Qwen 2.5, Llama 3, BGE embeddings).

#### Request Example (cURL)

```bash
curl -X GET "https://stampede3.tacc.utexas.edu:60055/v1/models" \
     -H "Authorization: Bearer flexserv" \
     -H "x-flexserv-token: flexserv" \
     --insecure
```

#### Response Payload (JSON)

```json
{
  "object": "list",
  "data": [
    {
      "id": "Qwen/Qwen2.5-7B-Instruct",
      "object": "model",
      "created": 1785440000,
      "owned_by": "flexserv"
    }
  ]
}
```

---

### B. Chat Completions API (`POST /v1/chat/completions`)

The primary endpoint used by `Instructor`, `OpenAI` client, and `test_generator.py` for structured curriculum, slide schema, and PyTorch code generation.

#### Request Body Payload Schema

```json
{
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert deep learning educator."
    },
    {
      "role": "user",
      "content": "Generate a PyTorch U-Net starter code snippet."
    }
  ],
  "temperature": 0.7,
  "top_p": 0.8,
  "max_tokens": 2048,
  "stream": false,
  "response_format": {
    "type": "json_object"
  }
}
```

#### Parameter Breakdown

* `model` (*string, required*): ID of the model (e.g., `Qwen/Qwen2.5-7B-Instruct`).
* `messages` (*array of objects, required*): List of role/content pairs (`system`, `user`, `assistant`).
* `temperature` (*float, optional*): Sampling temperature (`0.0` for deterministic, `0.7` default).
* `max_tokens` (*integer, optional*): Maximum tokens to generate.
* `response_format` (*object, optional*): Set `{"type": "json_object"}` for structured JSON generation.

#### Response Payload (JSON)

```json
{
  "id": "chatcmpl-flexserv123",
  "object": "chat.completion",
  "created": 1785440100,
  "model": "Qwen/Qwen2.5-7B-Instruct",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "```python\nimport torch\nimport torch.nn as nn\n..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 120,
    "completion_tokens": 250,
    "total_tokens": 370
  }
}
```

---

### C. Text Embeddings API (`POST /v1/embeddings`)

Generates vector embeddings for RAG retrieval engines (e.g., embedding textbook chapters or documentation chunks into Chroma/FAISS).

#### Request Body Payload Schema

```json
{
  "model": "BAAI/bge-small-en-v1.5",
  "input": [
    "Skip connections concatenate encoder feature maps to decoder layers.",
    "PyTorch Conv2d requires in_channels and out_channels."
  ]
}
```

#### Response Payload (JSON)

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.0124, -0.0431, 0.0891, "... 384 dimensions ..."]
    },
    {
      "object": "embedding",
      "index": 1,
      "embedding": [-0.0211, 0.0512, -0.0118, "... 384 dimensions ..."]
    }
  ],
  "model": "BAAI/bge-small-en-v1.5",
  "usage": {
    "prompt_tokens": 24,
    "total_tokens": 24
  }
}
```

---

### D. Audio Transcription API (`POST /v1/audio/transcriptions`)

Transcribes audio lectures or voice notes into text using served Whisper models.

#### Request Format (`multipart/form-data`)

```bash
curl -X POST "https://stampede3.tacc.utexas.edu:60055/v1/audio/transcriptions" \
     -H "Authorization: Bearer flexserv" \
     -H "x-flexserv-token: flexserv" \
     -F "file=@lecture_audio.mp3" \
     -F "model=openai/whisper-large-v3" \
     --insecure
```

#### Response Payload (JSON)

```json
{
  "text": "Welcome to week 3 of Applied Deep Learning. Today we will discuss U-Net skip connections."
}
```

---

### E. Vision & Object Detection API (`POST /v1/vision` or `/v1/yolo`)

Performs object detection, bounding box extraction, or image feature attribution using served vision models (YOLO / SAM / Vision Transformers).

#### Request Body Payload Schema (JSON)

```json
{
  "model": "ultralytics/yolov8x",
  "image_url": "https://example.org/medical_scan.jpg",
  "confidence_threshold": 0.5
}
```

#### Response Payload (JSON)

```json
{
  "predictions": [
    {
      "class": "lesion",
      "confidence": 0.92,
      "bbox": [120, 85, 340, 290]
    }
  ]
}
```

---

## 4. Python Request Implementation Templates

### Using `requests` Library

```python
import urllib3
import requests

urllib3.disable_warnings()

url = "https://stampede3.tacc.utexas.edu:60055/v1/chat/completions"
headers = {
    "Authorization": "Bearer flexserv",
    "x-flexserv-token": "flexserv",
    "Content-Type": "application/json"
}

payload = {
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [
        {"role": "user", "content": "Explain U-Net skip connections in 2 sentences."}
    ],
    "max_tokens": 150
}

response = requests.post(url, headers=headers, json=payload, verify=False)
print(response.json()["choices"][0]["message"]["content"])
```

### Using `OpenAI` SDK Client

```python
import httpx
from openai import OpenAI

client = OpenAI(
    base_url="https://stampede3.tacc.utexas.edu:60055/v1",
    api_key="flexserv",
    default_headers={"x-flexserv-token": "flexserv"},
    http_client=httpx.Client(verify=False)
)

completion = client.chat.completions.create(
    model="Qwen/Qwen2.5-7B-Instruct",
    messages=[
        {"role": "user", "content": "Explain U-Net skip connections in 2 sentences."}
    ]
)

print(completion.choices[0].message.content)
```
