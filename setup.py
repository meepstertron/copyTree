from setuptools import setup, find_packages

setup(
    name='copytree',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'copytree=copytree.main:main',
            'ct=copytree.main:main',
        ],
    },
)