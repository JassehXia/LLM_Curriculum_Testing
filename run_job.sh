#!/bin/bash
#SBATCH --job-name=qwen_curriculum
#SBATCH --account=PAS2699
#SBATCH --gpus=1
#SBATCH --time=01:00:00
#SBATCH --output=/fs/ess/PAS2699/jseh_workspace/LLM_Curriculum_Testing/slurm_%j.log
#SBATCH --error=/fs/ess/PAS2699/jseh_workspace/LLM_Curriculum_Testing/slurm_%j.err

# Ensure outputs directory exists
mkdir -p outputs

# 1. Spin up local vLLM server on the allocated GPU compute node
echo "Starting vLLM server on port 8000..."
vllm serve Qwen/Qwen2.5-3B-Instruct --port 8000 &
VLLM_PID=$!

# 2. Wait until vLLM is ready to accept requests
echo "Waiting for vLLM server endpoint..."
until curl -s http://localhost:8000/v1/models > /dev/null; do
    sleep 5
done
echo "vLLM server ready!"

# 3. Execute generator pipeline
python test_generator.py

# 4. Clean up background vLLM process upon job completion
kill $VLLM_PID
