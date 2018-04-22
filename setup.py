from setuptools import setup

setup(
    name='turtlegit',
    packages=['turtlegit'],
    include_package_data=True,
    install_requires=[
        'flask',
        'rdflib'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)