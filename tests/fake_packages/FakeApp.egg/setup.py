from setuptools import setup, find_packages

setup(
    name="FakeApp",
    version="1.0",
    packages=find_packages(),
    entry_points={
        'cli.commands': [
            'target = fakeapp.commands',
        ]
    },
)
