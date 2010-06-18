# vim:ts=4:sts=4:sw=4:expandtab
import new
from satori.objects import DispatchOn
from django.db import models
from django.db.models.fields.related import add_lazy_relation
from satori.ars.model import Contract, Procedure, Parameter, TypeAlias, Void, Boolean, Int32, Int64, String
from satori.ars.naming import Name, ClassName, MethodName, FieldName, AccessorName, ParameterName, NamingStyle

id_types = {}
array_types = {}
#struct_types = {}

def get_id_type(model):
    if isinstance(model, models.base.ModelBase):
    	model = model._meta.object_name
    if not model in id_types:
        id_types[model] = TypeAlias(name=Name(ClassName(model + 'Id')), target_type=Int64)
    return id_types[model]

def get_array_type(model):
    if isinstance(model, models.base.ModelBase):
    	model = model._meta.object_name
    if not model in array_types:
        array_types[model] = ListType(name=Name(ClassName(model + 'IdList')), element_type=get_id_type(model))
    return array_types[model]

#def get_struct_type(model):
#    ?

class OperProvider(object):
    def _add_opers(self, opers):
        raise NotImplementedError()

@DispatchOn(field=object)
def gen_field_opers(model, field):
    return []

@DispatchOn(field=models.AutoField)
def gen_field_opers(model, field):
    return []

@DispatchOn(field=models.ForeignKey)
def gen_field_opers(model, field):
    field_name = field.name
    other = field.rel.to
    ret = []

    def get(token, id):
        obj = model.objects.get(pk=id)
        return getattr(obj, field_name).id

    ret.append(FieldOper(model, field, 'get', get, get_id_type(other),
        (('token', String),('id', get_id_type(model)))))

    def set(token, id, value):
        other = set.func_dict['other']
        obj = model.objects.get(pk=id)
        other_obj = other.objects.get(pk=value)
        setattr(obj, field_name, other_obj)
        obj.save()
        return value

    if isinstance(other, basestring):
        def resolve_related_class(func, model, cls):
            func.func_dict['other'] = model
        add_lazy_relation(model, set, other, resolve_related_class)
    else:
        set.func_dict['other'] = other

    ret.append(FieldOper(model, field, 'set', set, get_id_type(other), 
        (('token', String), ('id', get_id_type(model)), ('value', get_id_type(other)))))
#    ret.append(FieldOper(model, field, 'set', set, Void, 
#        (('token', String), ('id', get_id_type(model)), ('value', get_id_type(other)))))

    return ret

@DispatchOn(field=models.IntegerField)
def gen_field_opers(model, field):
    field_name = field.name
    ret = []

    def get(token, id):
        obj = model.objects.get(pk=id)
        return getattr(obj, field_name)

    ret.append(FieldOper(model, field, 'get', get, Int32,
        (('token', String),('id', get_id_type(model)))))

    def set(token, id, value):
        obj = model.objects.get(pk=id)
        setattr(obj, field_name, value)
        obj.save()
        return value

    ret.append(FieldOper(model, field, 'set', set, Int32, 
        (('token', String), ('id', get_id_type(model)), ('value', Int32))))
#    ret.append(FieldOper(model, field, 'set', set, Void, 
#        (('token', String), ('id', get_id_type(model)), ('value', Int32))))

    return ret

@DispatchOn(field=models.CharField)
def gen_field_opers(model, field):
    field_name = field.name
    ret = []

    def get(token, id):
        obj = model.objects.get(pk=id)
        return getattr(obj, field_name)

    ret.append(FieldOper(model, field, 'get', get, String, 
        (('token', String),('id', get_id_type(model)))))

    def set(token, id, value):
        obj = model.objects.get(pk=id)
        setattr(obj, field_name, value)
        obj.save()
        return value

#    ret.append(FieldOper(model, field, 'set', set, Void, 
#        (('token', String), ('id', get_id_type(model)), ('value', String))))
    ret.append(FieldOper(model, field, 'set', set, String, 
        (('token', String), ('id', get_id_type(model)), ('value', String))))

    return ret

class FieldOper(object):
    def __init__(self, model, field, name, implement, return_type, parameters):
        self._model = model
        self._field = field
        self._name = name

        self._ars_name = Name(ClassName(model._meta.object_name), FieldName(field.name), AccessorName(name))
        self._ars_parameters = parameters
        self._ars_return_type = return_type

        self._want = True
        self._can = None
        self._implement = implement

    def can(self, proc):
        self._can = proc
        return proc

    def want(self, value):
        self._want = value

    def implement(self, proc):
        self._implement = proc
        return proc

    def _add_opers(self, opers):
        if not self._want:
            return

        can = self._can
        implement = self._implement

        if can:
            def func(*args, **kwargs):
                can(*args, **kwargs)
                return implement(*args, **kwargs)
        else:
            def func(*args, **kwargs):
                return implement(*args, **kwargs)

        func.__name__ = NamingStyle.PYTHON.format(self._ars_name)
        func.func_name = func.__name__

        proc = Procedure(name=self._ars_name, return_type=self._ars_return_type, implementation=func)
        for param in self._ars_parameters:
            proc.addParameter(Parameter(name=Name(ParameterName(param[0])), type=param[1]))

        opers.append(proc)

class FieldOpers(object):
    def __init__(self, model, field):
        self._model = model
        self._field = field

        self._opers = gen_field_opers(model, field)

        for oper in self._opers:
            setattr(self, oper._name, oper)

    def _add_opers(self, opers):
        for oper in self._opers:
            oper._add_opers(opers)

contracts = []

class MethodOper(object):
    def __init__(self, name, return_type, parameters):
        self._name = name
        self._ars_parameters = parameters
        self._ars_return_type = return_type
        self._implement = None

    def __call__(self, function):
        self._implement = function
        return function

    def _add_opers(self, opers):
        if self._implement:
            implement = self._implement

            self._ars_name = Name(ClassName(self._name), MethodName(implement.func_name))

            def func(*args, **kwargs):
                return implement(*args, **kwargs)

            func.__name__ = NamingStyle.PYTHON.format(self._ars_name)
            func.func_name = func.__name__

            proc = Procedure(name=self._ars_name, return_type=self._ars_return_type, implementation=func)
            for param in self._ars_parameters:
                proc.addParameter(Parameter(name=Name(ParameterName(param[0])), type=param[1]))

            opers.append(proc)

class ModelOpers(OperProvider):
    def __init__(self, model):
        self._model = model
        self._field_operss = []
        self._method_opers = []
        for field in model._meta.fields:
            field_opers = FieldOpers(model, field)
            self._field_operss.append(field_opers)
            setattr(self, field.name, field_opers)

    def method(self, return_type, parameters):
        mo = MethodOper(self._model._meta.object_name, return_type, parameters)
        self._method_opers.append(mo)
        return mo

    def _add_opers(self, opers):
        contract = Contract(name=Name(ClassName(self._model._meta.object_name)))
        contracts.append(contract)

        myopers = []
        for field_opers in self._field_operss:
            field_opers._add_opers(myopers)
            
        for method_opers in self._method_opers:
            method_opers._add_opers(myopers)
            
        for oper in myopers:
            contract.addProcedure(oper)

        opers.extend(myopers)

class StaticOpers(OperProvider):
    def __init__(self, name):
        self._name = name
        self._method_opers = []

    def method(self, return_type, parameters):
        mo = MethodOper(self._name, return_type, parameters)
        self._method_opers.append(mo)
        return mo

    def _add_opers(self, opers):
        contract = Contract(name=Name(ClassName(self._name)))
        contracts.append(contract)

        myopers = []
        for method_opers in self._method_opers:
            method_opers._add_opers(myopers)
            
        for oper in myopers:
            contract.addProcedure(oper)

        opers.extend(myopers)
    

class OpersBase(type):
    def __new__(cls, name, bases, dict_):
        opers = []

        for elem in dict_.itervalues():
            if isinstance(elem, OperProvider):
                elem._add_opers(opers)

        newdict = {}

        for oper in opers:
            newdict[NamingStyle.PYTHON.format(oper.name)] = staticmethod(oper.implementation)

        return super(OpersBase, cls).__new__(cls, name, bases, newdict)

    def __init__(cls, name, bases, dict_):
        super(OpersBase, cls).__init__(name, bases, dict_)

class Opers(object):
    __metaclass__ = OpersBase
