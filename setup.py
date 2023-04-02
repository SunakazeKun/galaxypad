import setuptools
from galaxypad import __version__, __author__

with open("README.md", "r") as f:
    README = f.read()

setuptools.setup(
    name="galaxypad",
    version=__version__,
    author=__author__,
    url="https://github.com/SunakazeKun/galaxypad",
    description="Python tool to record PAD playback for Super Mario Galaxy 2",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords=["nintendo", "super-mario-galaxy-2", "pad", "dolphin", "modding"],
    packages=setuptools.find_packages(),
    install_requires=["dolphin_memory_engine"],
    python_requires=">=3.10",
    license="gpl-3.0",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3 :: Only"
    ],
    entry_points={
        "console_scripts": [
            "galaxypad = galaxypad.__main__:main"
        ]
    }
)
