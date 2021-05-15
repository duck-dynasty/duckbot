import os

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install


def download_nltk_data():
    import nltk

    venv = os.getenv("VIRTUAL_ENV")
    base = venv if venv else os.getenv("HOME")
    download_dir = os.path.join(base, "nltk_data")
    nltk.download("cmudict", download_dir=download_dir)


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
        url="https://github.com/Chippers255/duckbot",
        python_requires=">=3.8",
        packages=find_packages(),
        cmdclass={"develop": PostDevelop, "install": PostInstall},
        setup_requires=["nltk>=3.6,<4"],
        install_requires=[
            "discord.py[voice]>=1.7,<2",
            "beautifulsoup4",
            "pytz",
            "holidays>=0.11,<0.12",
            "pyowm>=3.2,<4",  # openweather
            "psycopg2",
            "sqlalchemy>=1.4,<2",
            "d20>=1.1.0,<2",
            "nltk>=3.6,<4",
        ],
        extras_require={
            "dev": [
                "pytest",
                "pytest-asyncio",
                "pytest-mock",
                "pytest-xdist[psutil]",
                "flake8",
                "pytest-flake8",
                "black",
                "pytest-black",
                "isort",
                "pytest-isort",
                "pytest-blockage",
                "pytest-sugar",
                "pytest-icdiff",
                "pytest-cov",
            ]
        },
    )
