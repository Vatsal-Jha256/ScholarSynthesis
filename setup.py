"""
Setup script for LitReviewAgent package
"""

from setuptools import setup, find_packages

setup(
    name="litreview_agent",
    version="0.2.0",
    description="Agentic AI system for automated literature reviews",
    author="LitReviewAgent Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "vllm",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "litreview-agent=main:main",
        ],
    },
) 