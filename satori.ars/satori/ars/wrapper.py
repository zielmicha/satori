# vim:ts=4:sts=4:sw=4:expandtab

import collections
import datetime
import time
import types
import sys
import copy
from satori.objects import Signature, Argument, ArgumentMode, ReturnValue, ConstraintDisjunction, TypeConstraint
from satori.ars.model import NamedTuple, TypeAlias, ListType, MapType, Structure, Procedure, Contract, Void, Int32, Int64, String, Boolean

class TypedListType(type):
    def __new__(mcs, name, bases, dict_):
        elem_type = dict_['elem_type']
        name = 'list[' + str(elem_type) + ']'
        return type.__new__(mcs, name, bases, dict_)

    def __instancecheck__(cls, obj):
        if not isinstance(elem, collections.Sequence):
            return False

        for elem in obj:
            if not isinstance(elem, cls.elem_type):
                return False

        return True

    def ars_type(cls):
        if not hasattr(cls, '_ars_type'):
            cls._ars_type = ListType(python_to_ars_type(cls.elem_type))

        return cls._ars_type


def TypedList(elem_type):
    return TypedListType('', (), {'elem_type': elem_type})


class TypedMapType(type):
    def __new__(mcs, name, bases, dict_):
        key_type = dict_['key_type']
        value_type = dict_['value_type']
        name = 'map[' + str(key_type) + ',' + str(value_type) + ']'
        return type.__new__(mcs, name, bases, dict_)

    def __instancecheck__(cls, obj):
        if not isinstance(elem, collections.Mapping):
            return False

        for (key, value) in obj.items:
            if not isinstance(key, cls.key_type):
                return False
            if not isinstance(value, cls.value_type):
                return False

        return True

    def ars_type(cls):
        if not hasattr(cls, '_ars_type'):
            ars_key_type = python_to_ars_type(cls.key_type)
            ars_value_type = python_to_ars_type(cls.value_type)
            cls._ars_type = MapType(key_type=ars_key_type, value_type=ars_value_type)

        return cls._ars_type


def TypedMap(key_type, value_type):
    return TypedMapType('', (), {'key_type': key_type, 'value_type': value_type})


class StructType(type):
    def __new__(mcs, name, bases, dict_):
        assert 'fields' in dict_
        dict_['name'] = name
        return type.__new__(mcs, name, bases, dict_)

    def __instancecheck__(cls, obj):
        for (name, type_, optional) in cls.fields:
            if not ((name in obj) or optional):
                return False
            if name in obj:
                if not isinstance(obj[name], type_):
                    return False
        return True

    def ars_type(cls):
        if not hasattr(cls, '_ars_type'):
            cls._ars_type = Structure(name=cls.name)
            for (field_name, field_type, field_optional) in cls.fields:
                cls._ars_type.add_field(name=field_name, type=python_to_ars_type(field_type), optional=field_optional)

        return cls._ars_type


def Struct(name, fields):
    return StructType(name, (), {'fields': fields})


class DateTimeTypeAlias(TypeAlias):
    def __init__(self, ):
        super(DateTimeTypeAlias, self).__init__(name='DateTime', target_type=Int64)

    def needs_conversion(self):
        return True

    def convert_to_ars(self, value):
        if value is None:
            return None

        return long(time.mktime(value.timetuple()))

    def convert_from_ars(self, value):
        if value is None:
            return None

        return datetime.fromtimestamp(value)

python_basic_types = {
    types.NoneType: Void,
    types.IntType: Int32,
    types.LongType: Int64,
    types.StringType: String,
    types.BooleanType: Boolean,
    datetime.datetime: DateTimeTypeAlias(),
}

def python_to_ars_type(type_):
    if type_ in python_basic_types:
        return python_basic_types[type_]

    if hasattr(type_, 'ars_type'):
        return type_.ars_type()

    raise RuntimeError('Cannot convert type {0} to ars type.'.format(type_))


wrapper_list = []
contract_list = NamedTuple()
middleware = []

class Wrapper(object):
    @Argument('name', type=str)
    def __init__(self, name, parent):
        self._children = []
        self._name = name
        self._parent = parent
        self._want = True

        if parent is None:
            wrapper_list.append(self)

    def want(self, value):
        self._want = value

    def _add_child(self, child):
        self._children.append(child)
        setattr(self, child._name, child)

    def _generate_procedures(self):
        procs = {}
        ret = {}
        if not self._want:
            return ret

        for child in self._children:
            procs.update(child._generate_procedures())

        for (name, proc) in procs.iteritems():
            ret[self._name + '_' + name] = proc

        return ret

    def _fill_module(self, name):
        module = sys.modules[name]
    
        procs = self._generate_procedures()

        for (name, proc) in procs.iteritems():
            setattr(module, name, proc)

        setattr(module, '__all__', procs.keys())


def emptyCan(*args, **kwargs):
    return True


def emptyFilter(retval, *args, **kwargs):
    return retval


class ProcedureWrapper(Wrapper):
    @Argument('implement', type=types.FunctionType)
    def __init__(self, implement, parent):
        super(ProcedureWrapper, self).__init__(implement.__name__, parent)

        self._can = emptyCan
        self._filter = emptyFilter
        self._implement = implement

    def can(self, proc):
        self._can = proc
        return proc

    def filter(self, proc):
        self._filter = proc
        return proc

    def implement(self, proc):
        self._implement = proc
        return proc

    def _generate_procedures(self):
        ret = {}
        if not self._want:
            return ret

        can = self._can
        filter = self._filter
        implement = self._implement

        def proc(*args, **kwargs):
            if not can(*args, **kwargs):
                raise Exception('Access denied.')
            result = implement(*args, **kwargs)
            return filter(result, *args, **kwargs)

        Signature.of(implement).set(proc)
    
        ret[self._name] = proc

        def proc(*args, **kwargs):
            return can(*args, **kwargs)

        copy.copy(Signature.of(implement)).set(proc)
        Signature.of(proc).return_value = ReturnValue(type=bool)
    
        ret[self._name + '_can'] = proc

        return ret


class StaticWrapper(Wrapper):
    def __init__(self, name):
        super(StaticWrapper, self).__init__(name, None)

    def method(self, proc):
        self._add_child(ProcedureWrapper(proc, self))


class WrapperBase(type):
    def __new__(mcs, name, bases, dict_):
        newdict = {}

        for elem in dict_.itervalues():
            if isinstance(elem, Wrapper):
                for (name, proc) in elem._generate_procedures().iteritems():
                    newdict[name] = staticmethod(proc)
                    
        return type.__new__(mcs, name, bases, newdict)

class WrapperClass(object):
    __metaclass__ = WrapperBase

def is_nonetype_constraint(constraint):
    return isinstance(constraint, TypeConstraint) and (constraint.type == types.NoneType)

def extract_ars_type(constraint):
    if isinstance(constraint, ConstraintDisjunction):
        if len(constraint.members) == 2:
            if is_nonetype_constraint(constraint.members[0]):
                return (extract_ars_type(constraint.members[1])[0], True)
            elif is_nonetype_constraint(constraint.members[1]):
                return (extract_ars_type(constraint.members[0])[0], True)

    if isinstance(constraint, TypeConstraint):
        return (python_to_ars_type(constraint.type), False)

    raise RuntimeError("Cannot extract type from constraint: " + str(constraint))


def wrap(name, proc):
    signature = Signature.of(proc)

    (ars_ret_type, ars_ret_optional) = extract_ars_type(signature.return_value.constraint)

    arg_names = signature.positional
    arg_count = len(signature.positional)
    ars_arg_types = []
    ars_arg_optional = []
    arg_numbers = {}
    for i in range(arg_count):
        argument = signature.arguments[signature.positional[i]]
        (param_type, optional) = extract_ars_type(argument.constraint)
        optional = optional or (argument.mode == ArgumentMode.OPTIONAL)
        ars_arg_types.append(param_type)
        ars_arg_optional.append(optional)
        arg_numbers[signature.positional[i]] = i


    def reimplementation(*args, **kwargs):
        args = list(args)
    
        for i in middleware:
            i.process_request(args, kwargs)
        
        try:
            newargs = []
            newkwargs = {}
            for i in range(min(len(args), arg_count)):
                newargs.append(ars_arg_types[i].convert_from_ars(args[i]))

            for arg_name in kwargs:
                newkwargs[arg_name] = ars_arg_types[arg_numbers[arg_name]].convert_from_ars(kwargs[arg_name])

            ret = proc(*newargs, **newkwargs)

            ret = ars_ret_type.convert_to_ars(ret)
        except Exception as exception:
            for i in reversed(middleware):
                i.process_exception(args, kwargs, exception)
            raise
        else:
            for i in reversed(middleware):
                ret = i.process_response(args, kwargs, ret)
            return ret

    ars_proc = Procedure(name=name, implementation=reimplementation, return_type=ars_ret_type)

    for i in range(arg_count):
        ars_proc.add_parameter(name=signature.positional[i], type=ars_arg_types[i], optional=ars_arg_optional[i])

    return ars_proc

def generate_contract(wrapper):
    contract = Contract(name=wrapper._name)

    for (name, proc) in wrapper._generate_procedures().iteritems():
        contract.add_procedure(wrap(name, proc))

    return contract

def generate_contracts():
    if not contract_list.items:
        for wrapper in wrapper_list:
            contract_list.append(generate_contract(wrapper))

    return contract_list

def register_middleware(obj):
    middleware.append(obj)

