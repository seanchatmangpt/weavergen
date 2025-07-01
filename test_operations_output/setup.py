from setuptools import setup, find_packages

setup(
    name="generated-otel-package",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "opentelemetry-api",
        "opentelemetry-sdk",
    ],
)