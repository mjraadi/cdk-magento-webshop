import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="Magento Webshop",
    version="0.0.1",
    page="https://dev.to/mjraadi",
    license="MIT",
    description="A CDK app to provision the required resources to run a flexible, scalable and cost-effective Magento webshop on top of AWS. ",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Mohammadjavad Raadi",

    package_dir={"": "stacks"},
    packages=setuptools.find_packages(where="stacks"),

    install_requires=[
        "aws-cdk.core==1.131.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
