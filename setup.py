from setuptools import setup, find_packages

setup(
    name="warehouse-flow-simulator",
    version="0.1.0",
    description="A simulator for analyzing worker movement in warehouses",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/warehouse-flow-simulator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Logistics Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.2.0",
        "matplotlib>=3.4.0",
        "networkx>=2.6.0",
        "pillow>=8.0.0",
    ],
)
