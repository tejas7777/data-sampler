from setuptools import setup, find_packages

setup(
    name="datasampler",
    version="0.1",
    author="tejas",
    author_email="tejaschendekar2@gmail.com",
    long_description=open('README.md').read(),
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
    install_requires=[
        # List your project dependencies here
    ],
)