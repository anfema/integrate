"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
	name='integrate',
	version='1.3.0',
	description='Test framework for integration tests with dependencies',
	long_description=README,
	long_description_content_type='text/x-rst',
	url='https://github.com/anfema/integrate',
	author='Johannes Schriewer',
	author_email='hallo@dunkelstern.de',
	license='BSD',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
    	'Topic :: Software Development :: Testing',
    	'License :: OSI Approved :: BSD License',
    	'Programming Language :: Python :: 2.7',
    	'Programming Language :: Python :: 3.3',
    	'Programming Language :: Python :: 3.4',
    	'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6'
	],
	keywords='integration test tests',
	packages=find_packages(exclude=['docs', 'tests*']),
	install_requires=[
	],
	dependency_links=[
	]
)
