from setuptools import setup, find_packages

setup(
    name="colect-service",
    version="0.0.0",
    packages=find_packages(),
    install_requires=[
        'opcua',
        'pendulum',
        'pymongo',
        'python-dotenv',
        'pytest',
        'pytest-cov'
        'paho-mqtt',
    ],
    author="João Ícaro",
    author_email="joaoicaro@sistemaoraculos.com",
    description="Industrial data collection service with multi-industry support",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/oraculos-solutions/colect-service",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)