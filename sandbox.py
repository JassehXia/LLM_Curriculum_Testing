import sys
import os
import tempfile
import subprocess
from typing import Tuple

def clean_code_snippet(code: str) -> str:
    """ Remove markdown backticks from LLM code outputs."""
    s = code.strip()
    if s.startswith("```python"):
        s = s[9:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()

def run_in_sandbox(solution_code: str, unit_test: str, timeout: int = 120) -> Tuple[bool, str]:
    clean_solution = clean_code_snippet(solution_code)
    clean_test = clean_code_snippet(unit_test)

    # Ensure standard PyTorch imports are available if omitted by LLM
    imports_header = []
    full_text = f"{clean_solution}\n{clean_test}"
    if "import torch" not in full_text:
        imports_header.append("import torch")
    if "import torch.nn as nn" not in full_text:
        imports_header.append("import torch.nn as nn")
    if "import torch.nn.functional as F" not in full_text:
        imports_header.append("import torch.nn.functional as F")
    
    header_str = "\n".join(imports_header) + "\n\n" if imports_header else ""

    # Combine solution and unit test
    combined_script = f"{header_str}{clean_solution}\n\n# --- UNIT TEST ---\n{clean_test}"

    # Write script to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
        tmp_file.write(combined_script)
        tmp_path = tmp_file.name
    
    # Determine virtualenv Python executable if available
    python_exe = sys.executable
    venv_win = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
    venv_nix = os.path.join(os.getcwd(), ".venv", "bin", "python")
    if os.path.exists(venv_win):
        python_exe = venv_win
    elif os.path.exists(venv_nix):
        python_exe = venv_nix

    try:
        result = subprocess.run(
            [python_exe, tmp_path],
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
    

