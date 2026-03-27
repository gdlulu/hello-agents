import subprocess
import sys
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

# 脚本所在目录
script_dir = Path(__file__).resolve().parent

raw = subprocess.check_output(
    [sys.executable, "-m", "pip", "freeze"],
    text=True
).splitlines()

drop_prefixes = (
    "torch==",
    "torchvision==",
    "torchaudio==",
    "triton==",
    "nvidia-",
    "cuda-",
)

main_lines = []
for line in raw:
    s = line.strip()
    if not s or s.startswith("#"):
        continue
    if s.startswith(drop_prefixes):
        continue
    main_lines.append(s)

requirements_path = script_dir / "requirements.txt"
with open(requirements_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(main_lines) + "\n")

torch_lines = ["--index-url https://download.pytorch.org/whl/cu126"]

try:
    torch_ver = version("torch").split("+", 1)[0]
    torch_lines.append(f"torch=={torch_ver}")
except PackageNotFoundError:
    torch_lines.append("torch==2.7.1")

requirements_torch_path = script_dir / "requirements.torch.txt"
with open(requirements_torch_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(torch_lines) + "\n")

print(f"generated: {requirements_path}, {requirements_torch_path}")