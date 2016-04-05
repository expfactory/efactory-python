from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

setup(
    # Application name:
    name="expfactory",

    # Version number (initial):
    version="2.5.20",

    # Application author details:
    author="Vanessa Sochat",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),

    # Data files
    include_package_data=True,
    zip_safe=False,

    # Details
    url="http://www.github.com/expfactory",

    license="LICENSE",
    description="Python module for managing experiment factory experiments, for deployment to a psiturk battery or docker container.",
    keywords='psiturk behavior neuroscience experiment factory docker',

    install_requires = ['numpy','Flask','gitpython','flask-restful','selenium','cognitiveatlas','scipy','numexpr','seaborn'],

    entry_points = {
        'console_scripts': [
            'expfactory=expfactory.scripts:main',
        ],
    },

)
