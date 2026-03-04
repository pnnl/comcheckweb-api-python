import subprocess
from pathlib import Path


def run_scripts(base_dir: str = "scripts"):
    base_path = Path(base_dir)

    if not base_path.exists():
        raise FileNotFoundError(f"Directory '{base_dir}' does not exist.")

    scripts = sorted(base_path.rglob("*_script.py"))

    if not scripts:
        print("No *_script.py files found.")
        return

    for script in scripts:
        print(f"Running: {script}")
        result = subprocess.run(["python", str(script)], capture_output=True, text=True)

        print("---- OUTPUT ----")
        print(result.stdout)
        print("---- ERRORS ----")
        print(result.stderr)
        print("----------------")
        print()


if __name__ == "__main__":
    run_scripts()
