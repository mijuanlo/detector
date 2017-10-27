import os
import sys
import importlib
import inspect
import utils.log as log

log.debug("File "+__name__+" loaded")

def load_module(module_path, filename):
    """ returns the module if filename is a module else None """
    if filename.endswith('.py'):
        module = filename[:-3]
    elif os.path.exists(os.path.join(module_path, filename, '__init__.py')):
        module = filename
    else:
        return None
    try:
        return importlib.import_module(module)
    except:
        log.exception('Loading %s failed.' % module)
        return None

class PluginManager(object):
    def __init__(self):
        self.found_duplicates=False
        self.modules = {}
        self.classes = {}
        self.found = []

    def add_path(self, module_path,typeobj=object):
        sys.path.append(module_path)
        for filename in os.listdir(module_path):
            module = load_module(module_path, filename)
            if module:
                if module.__name__ in self.modules:
                    log.error("Duplicated module found {} unable to continue processing".format(module.__name__))
                    self.found_duplicates=True
                    continue
                self.modules[module.__name__] = module
                self._extract_classes(module,typeobj)
        sys.path.remove(module_path)
        log.info("Found {} plugins: {}".format(len(self.found),','.join(self.found)))

    def _extract_classes(self, module,typeobj):
        for name in dir(module):
            obj = getattr(module, name)
            if inspect.isclass(obj):
                #if hasattr(obj, '_VERSION') and obj._VERSION != None and issubclass(obj,typeobj):
                if issubclass(obj, typeobj) and obj != typeobj:
                    #version = getattr(obj, '_VERSION')
                    #log.info("Found plugin: %s.%s %s" % (module.__name__, name, version))
                    if name in self.classes:
                        log.error("Duplicated class {} found into module {}, unable to add".format(name,module.__name__))
                        self.found_duplicates=True
                        continue
                    self.found.append("{}.{}".format(module.__name__, name))
                    self.classes[name] = obj


