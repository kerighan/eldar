import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="eldar",
    version="0.0.8",
    author="Maixent Chenebaux",
    author_email="max.chbx@gmail.com",
    description="Boolean text search in Python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/kerighan/eldar",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
)
