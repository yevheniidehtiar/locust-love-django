from setuptools import setup, find_packages

setup(
    name="http_header_profiling_middleware",
    version="0.1",
    packages=find_packages(),
    py_modules=["middleware"],
    install_requires=[
        "django>=5.0.0",
    ],
    description="HTTP Header Profiling Middleware for Django",
    author="Locust Love Django",
)
