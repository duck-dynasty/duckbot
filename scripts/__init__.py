import subprocess


def format():
    for tool in ["isort .", "black .", "mdformat .", "flake8 duckbot tests *.py", "mdformat --check duckbot tests wiki *.md"]:
        print(f"running `{tool}`")
        subprocess.run(tool, shell=True)
