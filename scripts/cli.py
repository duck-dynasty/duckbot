import os
import subprocess

import nltk
import textblob.download_corpora


def format():
    for tool in ["isort .", "black .", "mdformat .", "flake8 duckbot tests scripts", "mdformat --check duckbot tests wiki *.md"]:
        print(f"running `{tool}`")
        subprocess.run(tool, shell=True)


def setup_nltk():
    venv = os.getenv("VIRTUAL_ENV")
    base = venv if venv else os.getenv("HOME")
    download_dir = os.path.join(base, "nltk_data")

    original_download = nltk.download
    nltk.download = lambda x: original_download(x, download_dir=download_dir)

    print(f"Downloading NLTK data to: {download_dir}")
    nltk.download("cmudict")
    textblob.download_corpora.main()
