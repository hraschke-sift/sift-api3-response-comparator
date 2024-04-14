from setuptools import setup, find_packages

setup(
    name="api3-comparator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "typer==0.12.3",
        "requests==2.31.0",
        "deepdiff==7.0.0",
        "python-dotenv==1.0.1",
        "PyYAML==6.0.1",
        "rich==13.7.1",
    ],
    extras_require={
        "dev": [
            "black==24.3.0",
            "mypy-extensions==1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "api3-comparator=cli:app",
        ],
    },
)
