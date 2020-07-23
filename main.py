import jsonschema
import json
import os
import pathlib

dirpath = pathlib.Path().absolute()
base_schema_filename = "defs1.json"
base_schema_path = os.path.join(dirpath, "base", base_schema_filename)

with open(base_schema_path) as fd:
    base_schema = json.load(fd)

base_uri = f"http://example.com/schemas/defs1.json"

resolver = jsonschema.RefResolver(base_uri, base_schema)
validator = jsonschema.Draft7Validator(base_schema, resolver=resolver)

schema_filename = "schema.json"
schema_path = os.path.join(dirpath, schema_filename)

with open(schema_path) as fd:
    schema = json.load(fd)

example = {
    "product_id": "666",
    "amount": {"code": "xyz", "amount": 1.23}
}

validator.validate(example, schema)
