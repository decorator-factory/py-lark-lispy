import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylarklispy",
    version="0.0.1",
    author="decorator-factory",
    author_email="",
    description="Lisp-like language in pure Python w/ lark-parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/decorator-factory/py-lark-lispy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "lark-parser>=0.9.0",
        "pytest",
    ],
    python_requires='>=3.6',
)
