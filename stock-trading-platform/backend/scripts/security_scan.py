import subprocess
import sys


def run_cmd(cmd: list[str], label: str) -> bool:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  WARNINGS/ERRORS ({result.returncode}):")
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    if result.stderr:
        print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
    return result.returncode == 0


def main():
    print("Stoxly Security Audit")
    print("=====================")

    all_pass = True

    all_pass &= run_cmd(
        [sys.executable, "-m", "pip", "list", "--format=columns"],
        "1/5 Installed Packages",
    )

    all_pass &= run_cmd(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        "2/5 Running Tests",
    )

    try:
        all_pass &= run_cmd(
            [sys.executable, "-m", "bandit", "-r", "."],
            "3/5 Bandit Security Linter",
        )
    except FileNotFoundError:
        print("  [SKIP] bandit not installed (pip install bandit)")

    try:
        all_pass &= run_cmd(
            [sys.executable, "-m", "pip_audit", "--desc", "on"],
            "4/5 pip-audit Dependency Scan",
        )
    except FileNotFoundError:
        print("  [SKIP] pip-audit not installed (pip install pip-audit)")

    try:
        all_pass &= run_cmd(
            [sys.executable, "-m", "ruff", "check", ".", "--ignore", "E501"],
            "5/5 Ruff Lint Check",
        )
    except FileNotFoundError:
        print("  [SKIP] ruff not installed (pip install ruff)")

    print(f"\n{'='*60}")
    if all_pass:
        print("  ALL CHECKS PASSED")
    else:
        print("  SOME CHECKS FAILED")
    print(f"{'='*60}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
