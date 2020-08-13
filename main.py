import glob
import json
import jsonschema
import os
import pathlib
import sanic
import multiprocessing

from typing import Union

dirpath = str(pathlib.Path().absolute())


def _iter_nested(obj):
    """Iterate over all nested key, val pairs in a dictionary"""
    for key, val in obj.items():
        yield key, val, obj
        if isinstance(val, dict):
            for each in _iter_nested(val):
                yield each


def _format_schema(schema, data):
    schema = dict(schema)
    for key, val, nested in _iter_nested(schema):
        if key == '$id' or key == '$ref':
            try:
                nested[key] = val.format(**data)
            except KeyError:
                continue
    return schema


class SchemaServer:

    def __init__(self,
                 schemas_path: str,
                 base_uri: str,
                 schema_includes: dict,
                 sanic_config: dict,
                 app_name: str = "schemas"):
        # Mapping of path name to schema
        schemas = {}
        paths = os.path.join(schemas_path, "**", "*.json")
        for path in glob.iglob(paths, recursive=True):
            with open(path) as fd:
                schema = json.load(fd)
            includes = {**schema_includes, 'base': base_uri}
            subpath = os.path.relpath(path, schemas_path)
            schemas[subpath] = _format_schema(schema, includes)

        async def root(request, path: str = ''):
            if path not in schemas:
                return sanic.response.raw(b'', status=404)
            return sanic.response.json(schemas[path])
        app = sanic.Sanic(app_name)
        app.add_route(root, "/")
        app.add_route(root, "/<path:path>")
        app.run(**sanic_config)


class Validator:
    schema: dict

    def __init__(self,
                 schema: Union[str, dict],
                 base: str,
                 includes: dict):
        if isinstance(schema, str):
            with open(schema) as fd:
                schema = json.load(fd)
        if not base.startswith("file://"):
            base = "file://" + base
        self.schema = dict(schema)  # copy
        interps = {
            'base': base
        }
        for alias, uri in includes.items():
            interps[alias] = uri
        self.schema = _format_schema(schema, interps)

    def validate(self, example):
        jsonschema.validate(example, self.schema)


base_uri = 'http://localhost:5000'
server_args = ('remote', base_uri, {}, {'port': 5000})
server_proc = multiprocessing.Process(target=SchemaServer, args=server_args, daemon=True)
server_proc.start()

includes = {'remote1': base_uri}
validator = Validator("schema.json", dirpath, includes)

example = {
    "product_id": "666",
    "amount": {"code": "xyz", "amount": 1.23}
}
try:
    validator.validate(example)
except jsonschema.exceptions.ValidationError as err:
    print(err)
