import jsonschema
import os
import json

base_uri = f'file://{os.getcwd()}/'

with open('base.json') as fd:
    schema = json.load(fd)

# Create the resolver and validator
resolver = jsonschema.RefResolver(base_uri, schema)
validator = jsonschema.Draft7Validator(schema, resolver=resolver)

# Will get a validation error showing the schema from ref.json
try:
    validator.validate({})
except jsonschema.ValidationError as err:
    print(err)

try:
    validator.validate({"amount": 1, "product_id": 2})
except jsonschema.ValidationError as err:
    print(err)
