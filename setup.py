import re

from setuptools import find_packages, setup

from pathlib import Path


def read(filename):
    file_path = Path(__file__).parent / filename
    text_type = type(u"")
    with open(file_path, mode="r", encoding="utf-8") as f:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), f.read())


def get_requires():
    r_path = Path(__file__).parent / "requirements.txt"
    if r_path.exists():
        with open(r_path) as f:
            required = f.read().splitlines()
    else:
        required = []

    return required


setup(
    name="kanicounter",
    version="0.1.0",
    url="",
    license="MIT",
    author="fx-kirin",
    author_email="fx.kirin@gmail.com",
    description="Count events in rolling time windows and raise when limits are exceeded.",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    packages=find_packages(exclude=("tests",)),
    install_requires=get_requires(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
