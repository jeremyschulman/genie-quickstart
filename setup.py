
from setuptools import setup, find_packages

package_version = '0.1.0'
package_name = 'djinn'


def requirements(filename='requirements.txt'):
    return open(filename.strip()).readlines()


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name=package_name,
    version=package_version,
    description='pyATS Genie - demo extend parsers',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jeremy Schulman',
    packages=find_packages(),
    install_requires=requirements(),
    entry_points = {

        # for 'stampie'

        'stampie.plugins': [
            'phpIPAM = stampie.phpipam.plugin:plugin'
        ],

        # for IMNetDB

        'imnetdb_collections': [
            'mlags = stampie.db:MlagNodes'
        ],
        'imnetdb_database_models': [
            'stampie_db_model = stampie.db:stampie_db_model'
        ]
    }
)
