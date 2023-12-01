import os
import subprocess

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install


def run_code_formatters():
    for tool in ["isort .", "black .", "mdformat ."]:
        print(f"running `{tool}`")
        subprocess.run(tool, shell=True)


def download_nltk_data():
    import nltk
    import textblob.download_corpora

    venv = os.getenv("VIRTUAL_ENV")
    base = venv if venv else os.getenv("HOME")
    download_dir = os.path.join(base, "nltk_data")
    original_download = nltk.download
    nltk.download = lambda x: original_download(x, download_dir=download_dir)
    nltk.download("cmudict")
    textblob.download_corpora.main()


class PostDevelop(develop):
    def run(self):
        develop.run(self)
        self.execute(download_nltk_data, [], msg="Download NLTK Data")


class PostInstall(install):
    def run(self):
        install.run(self)
        self.execute(download_nltk_data, [], msg="Download NLTK Data")


if __name__ == "__main__":
    setup(
        name="duckbot",
        version="1.0",
        url="https://github.com/duck-dynasty/duckbot",
        python_requires=">=3.8",
        packages=find_packages(),
        cmdclass={"develop": PostDevelop, "install": PostInstall},
        install_requires=[
            "discord.py[voice]==2.3.2",
            "beautifulsoup4==4.12.2",
            "requests==2.31.0",
            "pytz==2023.3.post1",
            "timezonefinder==6.2.0",
            "holidays==0.35",
            "pyowm==3.3.0",  # openweather
            "psycopg2==2.9.9",
            "SQLAlchemy==2.0.22",
            "d20==1.1.2",
            "nltk==3.8.1",  # also in pyproject.toml, required for setup script above
            "textblob==0.17.1",  # also in pyproject.toml, required for setup script above
            "pyfiglet==0.8.post1",
            "matplotlib==3.7.2",
            "PyGithub==2.1.1",
            "wolframalpha==5.0.0",
            "yfinance==0.2.31",
        ],
        extras_require={
            "dev": [
                "pytest==7.4.3",
                "pytest-asyncio==0.21.1",
                "pytest-xdist[psutil]==3.3.1",
                "flake8==4.0.1",
                "black==23.10.1",
                "flake8-black==0.3.6",
                "isort==5.12.0",
                "flake8-isort==6.1.1",
                "pep8-naming==0.13.2",
                "pytest-flake8-v2==1.2.3",
                "mdformat==0.7.17",
                "mdformat-gfm==0.3.5",
                "mdformat-black==0.1.1",
                "responses==0.23.3",
                "pytest-blockage==0.2.4",
                "pytest-sugar==0.9.7",
                "pytest-icdiff==0.8",
                "pytest-cov==4.1.0",
                "pytest-lazy-fixture==0.6.3",
            ],
            "cdk": [
                "aws-cdk.core==1.204.0",
                "aws-cdk.aws-ec2==1.204.0",
                "aws-cdk.aws-ecs==1.204.0",
                "aws-cdk.aws-autoscaling==1.204.0",
                "aws-cdk.aws-efs==1.204.0",
                "aws-cdk.aws-iam==1.204.0",
                "aws-cdk.aws-logs==1.204.0",
                "aws-cdk.aws-ssm==1.204.0",
                "boto3==1.28.75",
            ],
        },
        entry_points={
            "console_scripts": [
                f"format = setup:{run_code_formatters.__name__} [dev]",
            ]
        },
    )
