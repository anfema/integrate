"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from setuptools import setup, find_packages

setup(
	name='integrate',
	version='1.2.0',
	description='Test framework for integration tests with dependencies',
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
