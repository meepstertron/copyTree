from setuptools import setup, find_packages

setup(
    name='copytree-cli',  
    version='0.1.2',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'copytree=copytree.main:main',  
            'ct=copytree.main:main',        
        ],
    },
    author='Meepsterton',
    author_email='jan.koch@hexagonical.ch',
    description='A tool to copy directory trees',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/meepstertron/copytree',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        # no dependencies
    ],
)