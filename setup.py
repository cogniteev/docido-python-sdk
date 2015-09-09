from setuptools import setup, find_packages

module_name = 'docido-python-sdk'
root_url = 'https://github.com/cogniteev/' + module_name

__version__ = None
exec(open('docido_sdk/__init__.py').read())

setup(
    name='docido-sdk',
    version=__version__,
    description='Docido software development kit for Python',
    author='Cogniteev',
    author_email='tech@cogniteev.com',
    url=root_url,
    download_url=root_url + '/tarball/' + __version__,
    license='Apache license version 2.0',
    keywords='cogniteev docido',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Natural Language :: English',
    ],
    packages=find_packages(exclude=['*.tests']),
    test_suite='docido.sdk.test.suite',
    zip_safe=True,
    install_requires=[
        'elasticsearch>=1.6.0',
        'Flask-OAuthlib>=0.8.0',
        'ProxyTypes==0.9',
        'setuptools>=0.6',
        'voluptuous>=0.8.7',
        'yamlious>=0.1.3',
    ],
    entry_points="""
        [console_scripts]
        dcc-run = docido_sdk.scripts.dcc_run:run
    """
)
