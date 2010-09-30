# vim:ts=4:sts=4:sw=4:expandtab
"""IDL writer for the Thrift protocol.
"""

from satori.objects import Argument, DispatchOn
from satori.ars.model import *

class ThriftWriter(object):
    """An ARS writer spitting out thrift IDL.
    """

    ATOMIC_NAMES = {
        ArsBoolean: 'bool',
        ArsInt8:    'byte',
        ArsInt16:   'i16',
        ArsInt32:   'i32',
        ArsInt64:   'i64',
        ArsFloat:   'double',
        ArsString:  'string',
        ArsVoid:    'void',
    }

    @DispatchOn(item=ArsElement)
    def _reference(self, item, target): # pylint: disable-msg=E0102
        raise RuntimeError("Unhandled Element type '{0}'".format(item.__class__.__name__))

    @DispatchOn(item=ArsNamedElement)
    def _reference(self, item, target): # pylint: disable-msg=E0102
        target.write(item.name)

    @DispatchOn(item=ArsAtomicType)
    def _reference(self, item, target): # pylint: disable-msg=E0102
        target.write(ThriftWriter.ATOMIC_NAMES[item])

    @DispatchOn(item=ArsList)
    def _reference(self, item, target): # pylint: disable-msg=E0102
        target.write('list<')
        self._reference(item.element_type, target)
        target.write('>')

    @DispatchOn(item=ArsMap)
    def _reference(self, item, target): # pylint: disable-msg=E0102
        target.write('map<')
        self._reference(item.key_type, target)
        target.write(',')
        self._reference(item.value_type, target)
        target.write('>')

    @DispatchOn(item=ArsSet)
    def _reference(self, item, target): # pylint: disable-msg=E0102
        target.write('set<')
        self._reference(item.element_type, target)
        target.write('>')

    @DispatchOn(item=ArsTypeAlias)
    def _write(self, item, target): # pylint: disable-msg=E0102
        target.write('typedef ')
        self._reference(item.target_type, target)
        target.write(' ')
        self._reference(item, target)
        target.write('\n')

    @DispatchOn(item=ArsStructure)
    def _write(self, item, target): # pylint: disable-msg=E0102
        target.write('struct ')
        self._reference(item, target)
        target.write(' {')
        sep = '\n\t'
        ind = 1
        for field in item.fields:
            target.write('{0}{1}:'.format(sep, ind))
            if field.optional:
                target.write('optional ')
            self._reference(field.type, target)
            target.write(' ')
            self._reference(field, target)
            sep = '\n\t'
            ind += 1
        target.write('\n}\n')

    @DispatchOn(item=ArsException)
    def _write(self, item, target): # pylint: disable-msg=E0102
        target.write('exception ')
        self._reference(item, target)
        target.write(' {')
        sep = '\n\t'
        ind = 1
        for field in item.fields:
            target.write('{0}{1}:'.format(sep, ind))
            if field.optional:
                target.write('optional ')
            self._reference(field.type, target)
            target.write(' ')
            self._reference(field, target)
            sep = '\n\t'
            ind += 1
        target.write('\n}\n')

    @DispatchOn(item=ArsConstant)
    def _write(self, item, target): # pylint: disable-msg=E0102
        #TODO
        pass

    @DispatchOn(item=ArsService)
    def _write(self, item, target): # pylint: disable-msg=E0102
        target.write('service ')
        self._reference(item, target)
        if item.base:
            target.write(' extends ')
            self._reference(item.base, target)
        target.write(' {')
        sep = '\n\t'
        for procedure in item.procedures:
            target.write(sep)
            self._reference(procedure.return_type, target)
            target.write(' ')
            self._reference(procedure, target)
            target.write('(')
            sep2 = ''
            ind = 1
            for parameter in procedure.parameters:
                target.write('{0}{1}:'.format(sep2, ind))
                if parameter.optional:
                    target.write('optional ')
                self._reference(parameter.type, target)
                target.write(' ')
                self._reference(parameter, target)
                sep2 = ', '
                ind += 1
            target.write(')')
            if procedure.exception_types:
                target.write(' throws (')
                sep2 = ''
                ind = 1
                for exception_type in procedure.exception_types:
                    target.write('{0}{1}:'.format(sep2, ind))
                    self._reference(exception_type.type, target)
                    target.write(' ')
                    self._reference(exception_type, target)
                    sep2 = ', '
                    ind += 1
                target.write(')')
            sep = '\n\t'
        target.write('\n}\n')

    def write_to(self, interface, target):
        for type in interface.types:
            self._write(type, target)

        for constant in interface.constants:
            self._write(constant, target)

        for service in interface.services:
            self._write(service, target)

