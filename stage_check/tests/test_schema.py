#!/usr/bin/env python3.6
###############################################################################
#
# | |_ ___  ___| |_     ___  ___| |__   ___ _ __ ___   __ _   _ __  _   _ 
# | __/ _ \/ __| __|   / __|/ __| '_ \ / _ \ '_ ` _ \ / _` | | '_ \| | | |
# | ||  __/\__ \ |_    \__ \ (__| | | |  __/ | | | | | (_| |_| |_) | |_| |
#  \__\___||___/\__|___|___/\___|_| |_|\___|_| |_| |_|\__,_(_) .__/ \__, |
#                 |_____|                                    |_|    |___/ 
#
# pytests for schema processing...
#
###############################################################################

import os
import jsonschema
import json
import pprint
import glob

import pytest


CONFIG_PATH = os.environ.get('SCHEMA_TEST_CONFIG_PATH', '../stage_check')

TEST_CONFIG_SCHEMA = os.path.join(CONFIG_PATH, "config_schema.json")
TEST_CONFIG = os.path.join(CONFIG_PATH, "config.json")

print(f"loading top-level schema {TEST_CONFIG_SCHEMA}... (expect exception on fail)\n")
with open(TEST_CONFIG_SCHEMA, "r") as schema_handle:
    json_schema = json.load(schema_handle)

print(f"loading top-level config {TEST_CONFIG}... (expect exception on fail)\n")
with open(TEST_CONFIG, "r") as config_handle:
    json_config = json.load(config_handle)

print(f"validate top-level config against schema... (expect exception on failure)\n")
valid = jsonschema.validate(json_config, json_schema, format_checker=jsonschema.FormatChecker())
print(f"validated successfully\n")



schema_files = glob.glob(os.path.join(CONFIG_PATH, "Schema*.json"))

@pytest.mark.parametrize('schema_file', schema_files)
def test_specific_schemas(schema_file):
    """
    Test all schemas to see if they load. config.json cannot be relied upon to 
    test validation of data against schemas because config.json may not include 
    all tests.  

    If json.load fails, an exception will be thrown and the test will fail...
    """
    print(f"Reading schema {schema_file}")
    with open(schema_file, "r") as schema_handle:
        json_schema = json.load(schema_handle)


