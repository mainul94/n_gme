from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in n_gme/__init__.py
from n_gme import __version__ as version

setup(
	name="n_gme",
	version=version,
	description="Customization for n Gme.",
	author="Mainul Islam",
	author_email="mainulkhan94@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
