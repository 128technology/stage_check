from setuptools import setup, find_packages
import os
import re
import pathlib

here = pathlib.Path(__file__).parent.resolve()
version_path=os.path.join(here, "stage_check", "_version.py")
print(f"Using {version_path} for __version__")

version = "Unknown"
version_line = ""
try:
   with open(version_path) as fh:
       version_line = fh.read()
except IOError:
   pass

matches = re.search(r"^\s*__version__\s*=\s*[\"'](.*?|.*?)[\"']", version_line)

if matches:
   try:
       version = matches.group(1)
   except IndexError:
       raise RuntimeError(f"Unable to parse {version_path}")
else:
   raise RuntimeError(f"Unable to extract version from {version_path}")

print(f"*** Setup Version: {version} ***")

setup(
    name='stage_check',
    description='Stage check for 128T deployment environment',
    version=version,
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
        'jmespath',
        'jsonschema',
        'lxml',
        'ncclient',
        'pytz',
        'requests',
        'sly',
        'version_utils',
        'jinja2'
    ]
)

