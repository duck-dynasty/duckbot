import subprocess


def main():
    for tool in ["isort .", "black .", "mdformat .", "flake8 duckbot tests scripts", "mdformat --check duckbot tests wiki *.md"]:
        print(f"running `{tool}`")
        subprocess.run(tool, shell=True)
