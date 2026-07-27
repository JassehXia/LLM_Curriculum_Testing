For this iteration, we are moving from templated practice, to a complete text based, LLM content generated based curriculum.

The Setup
The key is to have a constrained setup for deterministic output, while ensuring outputs are verified and tested on the fly. To do this we will be using
Qwen as the LLM for generation
Instructor for structured LLM input and output
Along with this, we can prompt again if any errors occur in the first generation
Python-pptx for slides generation

The User
The user can simply add in their own modules on the YAML config, for example:

“””
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
“””

The YAML Config
modules:
 id: and identifier for the module
 title: the title of the module
 week: define which week for the module to reside in
 context: gives more context as to what the educator wants to focus on
 difficulty: how difficult the given module will be; for implementing questions/todos

The Flow
Educator YAML Input: Provides module details like Title ("U-Net Skip Connections"), Level ("Sophomore"), and Context ("Focus on spatial loss").
Backend Prompt Expansion Engine:
Pulls actual pipeline metrics and artifacts (e.g., segmentation IoU score, dataset info).
Injects Bloom's Taxonomy and ABET outcomes.
Formats system prompt with exact Pydantic schemas.
Qwen: Processes the expanded prompt to generate structured JSON outputs.
SlideDeckSchema & DynamicExerciseSchema (JSON):
SlideDeck: Title, 3-4 formatted bullet points, and PyTorch code textboxes.
DynamicExercise: Instructions, starter code (TODOs), solution code, and unit tests (Asserts).
python-pptx Engine & Sandbox Verification Engine:
python-pptx: Builds the .pptx presentation deck.
Sandbox: Verifies the exercise by running the solution against the tests.
Final Output (Directory: Week_03/unet_segmentation/):
presentation.pptx
unet_segmentation_exercise.py
unet_segmentation_solution.py
unet_segmentation_test.py

Verification

Generation: Qwen generates the JSON containing solution_code and unit_test.
Validation: Pydantic runs a @field_validator on the solution_code.
Execution: A subprocess executes the solution_code against the unit_test.
Verification Outcome:
If Tests Pass: The process returns the validated object and proceeds to the pipeline.
If Tests Fail: The system raises a ValueError with an error log; the Instructor library catches the error, appends it to the prompt, and Qwen retries (up to 3 times).
