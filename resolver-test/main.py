import jsonschema
import os
import json
import urllib.request
import yaml

base_uri = f'file://{os.getcwd()}/'

with open('base.json') as fd:
    schema = json.load(fd)


class ExtendedRefResolver(jsonschema.RefResolver):

    def resolve_remote(self, uri):
        print('resolve_remote uri is', uri)
        with urllib.request.urlopen(uri) as content:
            content = content.read().decode("utf-8")
            if uri.endswith('.yaml') or uri.endswith('.yml'):
                result = yaml.safe_load(content)
            else:
                result = json.loads(content)

        if self.cache_remote:
            self.store[uri] = result
        return result


# Create the resolver and validator
resolver = ExtendedRefResolver(base_uri, schema)
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
