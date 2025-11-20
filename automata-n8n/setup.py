"""
Project Automata Setup Configuration

Install the package with:
    pip install -e .
"""

from setuptools import find_packages, setup

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="project-automata",
    version="2.0.0-alpha",
    author="Project Automata Team",
    description="Autonomous n8n workflow builder with AI-powered generation and community learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/drjlsmith10/n8er",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "scripts"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "api": [
            "praw>=7.7.0",  # Reddit API
            "google-api-python-client>=2.0.0",  # YouTube API
            "tweepy>=4.0.0",  # Twitter API
        ],
    },
    entry_points={
        "console_scripts": [
            "automata-research=scripts.run_web_research:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md"],
    },
)
