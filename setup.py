# coding:utf-8

from setuptools import find_packages, setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='mango-ttic',  
    version='1.0',   
    author='ttic',  
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Oaklight/mango/tree/camera_ready",    
    packages=find_packages(),
    python_requires='>=3.11',
    install_requires=[
        'packaging==24.0',
        'fire==0.6.0',
        'networkx==3.2.1',
        'matplotlib==3.7.1',
        'pandas==2.2.1',
        'scipy==1.12.0',
    ],

)

