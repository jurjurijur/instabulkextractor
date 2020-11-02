import setuptools
from pathlib import Path

setuptools.setup(
    name="instabulkextractor",
    version="0.1.0",
    description=('search accounts matching keywords and extract media'),
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    license="MIT",
    maintainer="jurjurijur",
    author='jurjurijur',
    url='https://github.com/jurjurijur/instabulkextractor.git',
    install_requires=[
        'requests>=2.21.0',
        'python-slugify==3.0.2',
        'pyfiglet==0.8.post1',     
        'argparse==1.2.1', 
    ],
    classifiers=[
        'Development Status :: 1 - ALPHA   ',
        'Operating System :: OS Independent',
        'Licence :: MIT license',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
)
