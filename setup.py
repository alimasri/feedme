import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="feedme-alimasri91",
    version="1.0.0",
    author="Ali Masri",
    author_email="alimasridev@gmail.com",
    description="Automated email campaign using XML Feed",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alimasri/feedme",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
