from setuptools import find_packages, setup

setup(
    name='HamsterTracSyncr', version='1.0.0',
    packages=find_packages(exclude=['*.tests*']),
    scripts=['scripts/hamster-syncr', 'scripts/hamster-syncr-reset-tags'],
    install_requires=[]
)