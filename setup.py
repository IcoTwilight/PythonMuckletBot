import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "Mucklet",
    version = "1.0.9",
    author = "Ico Twilight",
    author_email = "Ico@duck.com",
    description = "A package for creating and using bots for the Mucklet role-playing service.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/IcoTwilight/PythonMuckletBot",
    project_urls = {
        "Bug Tracker": "https://github.com/IcoTwilight/PythonMuckletBot/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    install_requires=[
          'websocket-client',
          'bson',
    ],
    python_requires = ">=3.6"
)
