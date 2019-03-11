import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rest_locust",
    version="0.0.1",
    author="Partha Saradhi Konda",
    author_email="parthasaradhi1992@gmail.com",
    description="Rest Locust for load testing the rest end points using locustio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/parthakonda/rest_locust",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "locustio==0.9.0",
        "Jinja2==2.10",
        "coverage==4.5.1"
    ],
)
