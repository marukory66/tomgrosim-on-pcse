from setuptools import setup, find_packages

DESCRIPTION = "tomatomato: Predicts tomato yield using actual measured photosynthesis or photosynthesis predicted from environmental information."
NAME = 'tomatomato'
AUTHOR = 'Naomichi Fujiuchi,Ryoga Maruko'
AUTHOR_EMAIL = 'wlingwo@gmail.com'
URL = 'https://github.com/marukory66/tomgrosim-on-pcse/tree/develop'
LICENSE = 'GPL3'
DOWNLOAD_URL = 'https://github.com/marukory66/tomgrosim-on-pcse/tree/develop'
VERSION = "1.0.0"

INSTALL_REQUIRES = [
    'SQLAlchemy>=1.3.0, <2.0',
    'PyYAML>=5.1',
    'openpyxl>=3.0.0',
    'requests>=2.0.0',
    'pandas>=0.25',
    'traitlets-pcse==5.0.0.dev',
]


CLASSIFIERS = [
    'Intended Audience :: Science/Research',
    'License :: GPL3',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3 :: Only',

]

setup(name=NAME,
    author=AUTHOR,
    author_email = AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    version=VERSION,
    download_url=DOWNLOAD_URL,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    classifiers=CLASSIFIERS
    )