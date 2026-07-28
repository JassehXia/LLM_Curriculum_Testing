import sys
import os
import tempfile
import subprocess
from typing import Tuple

def clean_code_snippet(code: str) -> str:
    """ Remove markdown backticks from LLM code outputs."""
    lines = code.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()

def run_in_sandbox(solution_code: str, unit_test: str, timeout: int = 120) -> Tuple[bool, str]:
    clean_solution = clean_code_snippet(solution_code)
    clean_test = clean_code_snippet(unit_test)

    # Combine solution and unit test
    combined_script = f"{clean_solution}\n\n # --- UNIT TEST --- \n{clean_test}"

    # Write script to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
        tmp_file.write(combined_script)
        tmp_path = tmp_file.name
    
    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            error_msg = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            return False, error_msg

    except subprocess.TimeoutExpired:
        return False, f"Execution timed out after {timeout} seconds."
    except Exception as e:
        return False, f"Sandbox error: {str(e)}"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    

