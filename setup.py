from setuptools import setup, find_packages
from distutils.extension import Extension
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# C extension
extensions = [Extension("eldar", sources=["eldar/__init__.c"])]

setup(
    name="eldar",
    ext_modules=extensions,
    version="0.0.4",
    author="Maixent Chenebaux",
    author_email="mchenebaux@reputationsquad.com",
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
