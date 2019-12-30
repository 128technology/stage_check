from setuptools import setup, find_packages

setup(
    name='stage_check',
    description='Stage check for 128T deployment environment',
    version='1.0.0',
    python_requires='>=3.6',
    packages=find_packages(),
    package_data={
        'stage_check' : [ '*.json' ]
    },
    entry_points={
        'console_scripts': [
            'stage-check = stage_check.__main__:main'
        ]
    },
    install_requires=[
        'requests',
        'jmespath',
        'ncclient',
        'jsonschema',
        'lxml',
        'sly',
        'pytz'
    ]
)

