import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aqhi_canada",
    version="0.0.1",
    author="JM Lopez",
    author_email="s@jmll.me",
    description="Air Quality Health Index AQHI data from Environment Canada",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jm66/aqhi_canada",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests>=2.19.1",
        "geopy>=1.16.0",
        "requests_futures>=0.9.7",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
