from __future__ import annotations

import importlib
import platform
import shutil
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version


REQUIRED_PACKAGES = [
    "lerobot",
    "huggingface_hub",
    "matplotlib",
    "numpy",
    "pandas",
    "PIL",
]


def package_version(package_name: str) -> str:
    metadata_name = "pillow" if package_name == "PIL" else package_name
    try:
        return version(metadata_name)
    except PackageNotFoundError:
        return "unknown"


def check_import(package_name: str) -> bool:
    try:
        importlib.import_module(package_name)
        print(f"[OK] {package_name}: {package_version(package_name)}")
        return True
    except Exception as exc:
        print(f"[FAIL] {package_name}: {exc}")
        return False


def check_python() -> bool:
    current = sys.version_info
    ok = current >= (3, 10)
    status = "OK" if ok else "FAIL"
    print(f"[{status}] Python: {platform.python_version()} ({platform.system()} {platform.machine()})")
    if not ok:
        print("      This project uses lerobot==0.4.4, which requires Python >= 3.10.")
        print("      Create an isolated environment from environment.yml or use the Colab notebook.")
    return ok


def check_ffmpeg() -> bool:
    executable = shutil.which("ffmpeg")
    if not executable:
        print("[WARN] ffmpeg: not found on PATH")
        print("       Install through conda-forge: conda install ffmpeg -c conda-forge")
        return False

    try:
        output = subprocess.run(
            [executable, "-version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        first_line = output.stdout.splitlines()[0] if output.stdout else executable
        print(f"[OK] ffmpeg: {first_line}")
        return True
    except Exception as exc:
        print(f"[WARN] ffmpeg: found but could not run version check: {exc}")
        return False


def check_lerobot_dataset_api() -> bool:
    candidates = [
        "lerobot.datasets.lerobot_dataset",
        "lerobot.common.datasets.lerobot_dataset",
    ]
    for module_name in candidates:
        try:
            module = importlib.import_module(module_name)
            getattr(module, "LeRobotDataset")
            print(f"[OK] LeRobotDataset API: {module_name}.LeRobotDataset")
            return True
        except Exception:
            continue
    print("[FAIL] LeRobotDataset API: could not import LeRobotDataset")
    return False


def main() -> int:
    print("Zero-Hardware Embodied AI environment check\n")

    required_checks = [check_python()]
    required_checks.extend(check_import(package) for package in REQUIRED_PACKAGES)
    required_checks.append(check_lerobot_dataset_api())

    optional_checks = [check_ffmpeg()]

    print("\nSummary")
    if all(required_checks):
        if not all(optional_checks):
            print("[WARN] Required Python packages are ready, but one optional system tool is missing.")
            print("       If video decoding fails later, install ffmpeg through conda-forge.")
        print("[OK] Environment is ready for the free project scripts.")
        return 0

    print("[FAIL] Environment is not ready yet. Fix the failed items above, then rerun python check_env.py.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
