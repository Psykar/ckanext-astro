from setuptools import setup, find_packages
import sys, os

version = '0.1a'

setup(
    name='resource_metadata',
    version=version,
    description="Parses a file on upload for additional metadata in the resource",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Joe Tsoi',
    author_email='joe.tsoi@okfn.org',
    url='',
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.resourcemetadata'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        # Add plugins here, e.g.
        resource_metadata=ckanext.resourcemetadata.plugin:ResourceMetadata
    ''',
)
