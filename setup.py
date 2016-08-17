import os
from setuptools import setup, find_packages
from setuptools.extension import Extension

with open('rio_alpha/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split('=')[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            break

long_description = """Rasterio plugin for handling nodata values

See https://github.com/mapbox/rio-alpha for docs."""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='rio-alpha',
    version=version,
    description=u"A replacement for pxm-alpha",
    long_description=long_description,
    classifiers=[],
    keywords='',
    url='https://github.com/mapbox/rio-alpha',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_date=True,
    zip_safe=False,
    install_requires=[
        'click',
        'numpy',
        'rasterio',
        'rasterio',
        'rio-mucho',
        'scikit-image'
        'scipy'
    ],
    extras_require={'test': [
        'codecov',
        'hypothesis',
        'pytest',
        'pytest-cov'
    ]},
    entry_points="""
    [rasterio.rio_plugins]
    islossy=rio_alpha.scripts.cli:islossy
    """
)
