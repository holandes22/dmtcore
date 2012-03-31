#!/usr/bin/env python
from setuptools import se,up, find_packages
import dmtcore

METADATA = dict(
    name='dmtcore',
    version=dmtcore.__version__,
    author='Pablo Klijnan',
    author_email='pabloklijnjan@gmail.com',
    description='',
    long_description='',
    url='http://github.com/holandes22/dmtcore',
    include_package_data=True,
    classifiers=[
        'Development Status :: 0 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe=False,
    packages=find_packages(),
    package_data={
        'dmtcore': []
    }
)

if __name__ == '__main__':
    setup(**METADATA)
