from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
MIN_PYTHON = (3, 10)
REQUIRED_MODULES = {
    "requests": "requests",
    "dotenv": "python-dotenv",
    "pandas": "pandas",
    "tabulate": "tabulate",
}


def check_runtime() -> dict[str, object]:
    missing = [package for module_name, package in REQUIRED_MODULES.items() if importlib.util.find_spec(module_name) is None]
    return {
        "python": sys.version.split()[0],
        "python_ok": sys.version_info >= MIN_PYTHON,
        "requirements_file": str(REQUIREMENTS_FILE),
        "missing": missing,
        "ok": sys.version_info >= MIN_PYTHON and not missing,
    }


def ensure_runtime(auto_install: bool = True) -> dict[str, object]:
    status = check_runtime()
    if status["ok"]:
        return status

    if not status["python_ok"]:
        raise RuntimeError(
            f"需要 Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+，当前是 {status['python']}。"
        )

    missing = list(status["missing"])
    if not auto_install:
        raise RuntimeError(
            "缺少依赖: " + ", ".join(missing) + f"。请运行: {sys.executable} -m pip install -r {REQUIREMENTS_FILE}"
        )

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)],
            check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("未找到 pip。请确认 Python 安装包含 pip。") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "自动安装依赖失败。请手动运行: "
            f"{sys.executable} -m pip install -r {REQUIREMENTS_FILE}"
        ) from exc

    final_status = check_runtime()
    if not final_status["ok"]:
        raise RuntimeError(
            "依赖安装后仍缺少: " + ", ".join(final_status["missing"])
        )
    return final_status


if __name__ == "__main__":
    import json

    print(json.dumps(check_runtime(), ensure_ascii=False, indent=2))
