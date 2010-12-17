# vim:ts=4:sts=4:sw=4:expandtab

# used in code generated by generate_attribute_group()
from types import NoneType

from satori.core.export import ExportClass, ExportModel, ExportMethod
from satori.core.export import BadAttributeType, Attribute, AnonymousAttribute, AttributeGroupField, DefaultAttributeGroupField
from satori.core.export import PCPermit, PCArg, PCGlobal, PCAnd, PCOr, PCEach, PCEachKey, PCEachValue, PCTokenUser, PCRawBlob
from satori.core.export import PCTokenIsUser, PCTokenIsMachine
from satori.core.export import token_container
from satori.core.export import Struct, DefineException, TypedList, TypedMap
from satori.core.export import DjangoId, DjangoStruct, DjangoIdList, DjangoStructList

def _load_models():
    import _ast
    import ast
    import os
    import re
    import sys

    from satori.core.export._topsort import topsort, CycleError

    modules = []

    entities_dir = os.path.join(os.path.split(__file__)[0], 'entities')

    for filename in os.listdir(entities_dir):
        if re.match(r'^[a-zA-Z][_a-zA-Z]*\.py$', filename):
            filename = os.path.join(entities_dir, filename)

            with open(filename, 'r') as f:
                moduleast = ast.parse(f.read(), filename)
                modulecode = compile(moduleast, filename, 'exec')

            provides = set()
            uses = set()

            for node in moduleast.body:
                if isinstance(node, _ast.Assign):
                    provides.update([x.id for x in node.targets])
                if isinstance(node, _ast.ClassDef):
                    provides.add(node.name)
                if isinstance(node, _ast.FunctionDef):
                    provides.add(node.name)
                if isinstance(node, _ast.ImportFrom):
                    if node.module == 'satori.core.models':
                        uses.update([x.name for x in node.names])

            modules.append((modulecode, uses, provides))
    
    pairs = []
    providers = {}

    for (code, uses, provides) in modules:
        for provide in provides:
            if provide in providers:
                print 'Two modules provide {0}'.format(provide)
                raise ImportError('Two modules provide {0}'.format(provide))
            providers[provide] = code
    
    for (code, uses, provides) in modules:
        for use in uses:
            if not use in providers:
                print 'No module provides {0}'.format(use)
                raise ImportError('No module provides {0}'.format(use))

            pairs.append((providers[use], code))

        # so isolated nodes are in the result
        pairs.append((None, code))

    try:
        codes = topsort(pairs)[1:]
    except CycleError:
        print 'There is a cycle in module dependencies'
        raise ImportError('There is a cycle in module dependencies')

    module = sys.modules[__name__]

    for code in codes:
        exec code in module.__dict__

    import satori.core.export
    import satori.core.export.oa
    import satori.core.export.pc
    import satori.core.export.type_helpers
    import satori.core.export.types_django
    import satori.core.export.token

    satori.core.export.init()
    satori.core.export.oa.init()
    satori.core.export.pc.init()
    satori.core.export.type_helpers.init()
    satori.core.export.types_django.init()
    satori.core.export.token.init()

_load_models()
