from setuptools import setup, find_packages

from os import path
from codecs import open
from datetime import date
from configparser import ConfigParser


def local_path(filename):
    return path.join(
        path.abspath(path.dirname(__file__)),
        filename)


# Get the long description from the README file
with open(local_path('README.md'), encoding='utf-8') as readme:
    long_description = readme.read()

# .build.info file must exist in the current directory and the
# build should fail if it does not.
# The file must contain build number in it.
# It is assumed that the file contains build number
# set by CI system. On local builds it should be 1.
with open(local_path('.build.info')) as build_info:
    build_number = build_info.read().strip()

today = date.today()
version = '{}.{}.{}'.format(today.year, today.month, build_number)

# Extract required packages and dev-packages from Pipfile
config = ConfigParser()
config.read(local_path('Pipfile'))
install_requires = [p.replace('"', '') for p in config['packages']]
dev_packages = [d.replace('"', '') for d in config['dev-packages']]

setup(
    name='pyqt-sql-demo',
    version=version,
    description='QWidget based PyQt query executor demo',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vduseev/pyqt-sql-demo',
    author='Vagiz Duseev',
    author_email='vagiz@duseev.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='pyqt sql demo sqlite qwidget qtableview',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        'dev': dev_packages
    },
    entry_points={
        'console_scripts': [
            'pyqt_sql_demo=pyqt_sql_demo:main',
        ]
    }
)
