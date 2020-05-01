import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = []
with open("requirements.txt", "r") as fh:
    for line in fh.readlines():
        requirements.append(line)

setuptools.setup(
    name="feedme",
    version="1.0.0",
    author="Ali Masri",
    author_email="alimasridev@gmail.com",
    description="Automated email campaign using XML Feed",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alimasri/feedme",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": ["feedme=feedme.__main__:run"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
