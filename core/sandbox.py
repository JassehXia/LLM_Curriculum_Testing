import sys
import os
import tempfile
import subprocess
from typing import Tuple

def clean_code_snippet(code: str) -> str:
    """Remove markdown backticks from LLM code outputs."""
    s = code.strip()
    if s.startswith("```python"):
        s = s[9:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()

def strip_fake_local_imports(code: str) -> str:
    """Filter out local module imports like 'from solution import ...' or 'from pytorch_basics_solution import ...'."""
    valid_lines = []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("from ") and " import " in stripped:
            if not any(stripped.startswith(f"from {pkg}") for pkg in ["torch", "typing", "unittest", "numpy", "math", "os", "sys"]):
                continue
        valid_lines.append(line)
    return "\n".join(valid_lines)

def run_in_sandbox(solution_code: str, unit_test: str, timeout: int = 120) -> Tuple[bool, str]:
    clean_solution = clean_code_snippet(solution_code)
    clean_test = strip_fake_local_imports(clean_code_snippet(unit_test))

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
            # HYBRID STATIC-DYNAMIC ANALYSIS: Extract failure line & code context from stack trace
            stderr = result.stderr
            script_lines = combined_script.splitlines()
            
            diagnostic_info = []
            for line in stderr.splitlines():
                if "line " in line and ".py" in line:
                    try:
                        parts = line.split("line ")
                        line_num = int(parts[1].split(",")[0].split()[0])
                        if 1 <= line_num <= len(script_lines):
                            code_at_line = script_lines[line_num - 1].strip()
                            diagnostic_info.append(f"• Exception at Line {line_num}: `{code_at_line}`")
                    except Exception:
                        pass
            
            diag_str = "\n".join(diagnostic_info) if diagnostic_info else "• See stack trace below for failure location."
            
            error_msg = (
                f"=== HYBRID RUNTIME DIAGNOSTIC ===\n"
                f"{diag_str}\n\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )
            return False, error_msg

    except subprocess.TimeoutExpired:
        return False, f"Execution timed out after {timeout} seconds."
    except Exception as e:
        return False, f"Sandbox error: {str(e)}"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
