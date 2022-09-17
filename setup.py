import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rapidomize", 
    version="0.7.5",
    author="rapidomize",
    author_email="contact@rapidomize.com",
    description="rapidomize python sdk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rapidomize/rapidomize-sdk-python.git",
    packages=['rapidomize'],
    # setuptools.find_packages(), #
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache-2.0",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    # python_requires='>=2.7,<3.0',
    install_requires=[
        'requests',
        'futures; python_version == "3"'
    ]
)