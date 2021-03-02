from setuptools import setup, find_packages

with open("readme.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["PyJWT>=2.0.1",
                "cryptography>=3.4.4",
                "requests>=2",
                "pandas>=1.1.5"]

setup(
    name="adobe_aam",
    version="0.0.2",
    author="Trevor McCormick",
    author_email="trevor.ryan.mccormick@gmail.com",
    description="Adobe Audience Manager API Python Extension",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/trevormccormick/adobe_aam_python/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
