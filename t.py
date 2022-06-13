from collections import defaultdict
import importlib
from importlib.metadata import version
import json
import logging
from pathlib import Path
import sys


def getversion(module):
    try:
        return module.__version__
    except AttributeError:
        try:
            return module.VERSION
        except AttributeError:
            try:
                return module.version()
            except AttributeError:
                return version(module)


logging.basicConfig(
    level=logging.WARN,
    filename="log.txt",
    filemode="a",
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt="%H:%M:%S",
)

def get_module_versions():
    module_versions = defaultdict(set)
    for path in sys.path:
        for module_path in Path(path).glob("*"):
            module_name = module_path.name
            if module_name.endswith(".dist-info"): # NOTE: Split out 'dist-info'
                module_name, *_ = module_name.rsplit("-", maxsplit=2)
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                logging.warning("Skipped: '%s' Error was '%s'", str(module_name), str(e))
            else:
                try:
                    module_version = getversion(module)
                except Exception as e:
                    logging.warning("Could not read version of module: '%s'. Error was: '%s'", str(module_name), str(e))
                else:
                    module_versions[module_name].add(module_version)

    module_versions_clean = sorted(
        {
            module_name: sorted(versions)
            for module_name, versions in module_versions.items()
        }.items()
    )
    return module_versions_clean

module_versions_clean = get_module_versions()

with open("versions.json", "w") as output_file:
    json.dump(
        obj=module_versions_clean,
        fp=output_file,
        indent=2,
    )
