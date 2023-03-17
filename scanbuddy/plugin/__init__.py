import importlib

def load(name):
    module = f'scanbuddy.plugin.{name}'
    try:
        return importlib.import_module(module).Plugin
    except:
        raise UnrecognizedPluginError(name)

class UnrecognizedPluginError(Exception):
    pass
