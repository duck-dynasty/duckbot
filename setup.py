import os

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install


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
            "discord.py[voice] @ git+https://github.com/Rapptz/discord.py",
            "beautifulsoup4",
            "requests>=2.26,<3",
            "pytz",
            "timezonefinder>=5.2,<6",
            "holidays>=0.11,<0.12",
            "pyowm>=3.2,<4",  # openweather
            "psycopg2",
            "sqlalchemy>=1.4,<2",
            "d20>=1.1.0,<2",
            "nltk>=3.6,<4",  # also in pyproject.toml, required for setup script above
            "textblob<1",  # also in pyproject.toml, required for setup script above
            "pyfiglet<1",
            "matplotlib>=3.4,<4",
            "PyGithub>=1.55,<2",
            "wolframalpha>=5,<6",
        ],
        extras_require={
            "dev": [
                "pytest",
                "pytest-asyncio",
                "pytest-xdist[psutil]",
                "flake8<5",
                "black",
                "flake8-black",
                "isort",
                "flake8-isort",
                "pep8-naming",
                "pytest-flake8",
                "responses>=0.14,<1",
                "pytest-blockage",
                "pytest-sugar",
                "pytest-icdiff",
                "pytest-cov",
            ]
        },
    )
