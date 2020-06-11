"""A setup tools based setup module"""
from setuptools import setup

from coaclient import __version__


def readme():
    """
    Return readme
    """
    with open('README.rst') as readme_file:
        return readme_file.read()


setup(
    name='coaclient',
    version=__version__,
    description='OAuth2.0 client for the Coursera App Platform.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
    keywords='coursera sdk cli tool oauth2',
    url='https://github.com/blittlemore-coursera/coaclient/',
    author='Ievgen Arbuznykov, Anton Makrushyn',
    author_email='xxxantikvarxxx@gmail.com, ansermak@gmail.com',
    license='Apache',
    entry_points={
        'console_scripts': [
            'coaclient = coaclient.main:main',
        ],
    },
    packages=[
        'coaclient',
        'coaclient.commands',
        'coaclient.cli',
        'coaclient.oauth2'
    ],
    install_requires=[
        'requests>=2.23.0',
        'semver>=2.9.0',
        'python-status==1.0.1'
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3'],
    include_package_data=True,
    zip_safe=False
)
