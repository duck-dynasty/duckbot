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
            "discord.py[voice] @ git+https://github.com/duck-dynasty/discord.py@2.0a-freeze",
            "beautifulsoup4==4.11.1",
            "requests==2.27.1",
            "pytz==2022.1",
            "timezonefinder==5.2.0",
            "holidays==0.13",
            "pyowm==3.3.0",  # openweather
            "psycopg2==2.9.3",
            "SQLAlchemy==1.4.36",
            "d20==1.1.2",
            "nltk==3.7",  # also in pyproject.toml, required for setup script above
            "textblob==0.17.1",  # also in pyproject.toml, required for setup script above
            "pyfiglet==0.8.post1",
            "matplotlib==3.5.1",
            "PyGithub==1.55",
            "wolframalpha==5.0.0",
            "yfinance==0.1.70",
        ],
        extras_require={
            "dev": [
                "pytest==7.1.2",
                "pytest-asyncio==0.18.3",
                "pytest-xdist[psutil]==2.5.0",
                "flake8==4.0.1",
                "black==22.3.0",
                "flake8-black==0.3.3",
                "isort==5.10.1",
                "flake8-isort==4.1.1",
                "pep8-naming==0.12.1",
                "pytest-flake8==1.1.1",
                "mdformat==0.7.14",
                "mdformat-gfm==0.3.5",
                "mdformat-black==0.1.1",
                "responses==0.20.0",
                "pytest-blockage==0.2.4",
                "pytest-sugar==0.9.4",
                "pytest-icdiff==0.5",
                "pytest-cov==3.0.0",
                "pytest-lazy-fixture==0.6.3",
            ],
            "cdk": [
                "aws-cdk.core==1.154.0",
                "aws-cdk.aws-ec2==1.154.0",
                "aws-cdk.aws-ecs==1.154.0",
                "aws-cdk.aws-autoscaling==1.154.0",
                "aws-cdk.aws-efs==1.154.0",
                "aws-cdk.aws-iam==1.154.0",
                "aws-cdk.aws-logs==1.154.0",
                "aws-cdk.aws-ssm==1.154.0",
                "boto3==1.22.4",
            ],
        },
        entry_points={
            "console_scripts": [
                f"format = setup:{run_code_formatters.__name__} [dev]",
            ]
        },
    )
