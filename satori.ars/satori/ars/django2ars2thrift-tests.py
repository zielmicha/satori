#vim:ts=4:sts=4:sw=4:expandtab
from unittest import TestCase

from satori.ars.naming import Name, ClassName, MethodName, ParameterName
from satori.ars.model import Contract, Procedure, Parameter, String, Int32
from satori.ars.thrift import ThriftWriter

from satori.ars.test_layer import DjangoTestLayer, setup_module
from satori.ars import django2ars
from django.db import models

setup_module(__name__)

class X(models.Model):
    __model__ = __name__ + '.models'

    a = models.IntegerField()
    b = models.CharField(max_length=12)

class OpX(django2ars.Opers):
    x = django2ars.ModelOpers(X)

    @x.method(String, (('par1', Int32), ('par2', String)))
    def func(par1, par2):
        return par1 + '_' + par2


class Y(models.Model):
    __model__ = __name__ + '.models'

    a = models.IntegerField()
    b = models.CharField(max_length=12)

class OpY(django2ars.Opers):
    y = django2ars.ModelOpers(Y)

    y.a.set.want(False)


class StaticOp(django2ars.Opers):
    s = django2ars.StaticOpers("BadOperations")

    @s.method(String, (('par1', Int32), ('par2', String)))
    def do_sth_stupid(par1, par2):
        return 'false'

    @s.method(String, (('par1', Int32), ('par2', String)))
    def do_sth_worse(par1, par2):
        return 'nothing'


# not verifying the result, only checking if runs without throwing exceptions

class Writer(TestCase):
    layer = DjangoTestLayer

    def setUp(self):
        self.text = None

    def clear(self):
        self.text = ''

    def write(self, data):
        self.text += data

    def testTrivial(self):
        self.clear()
        writer = ThriftWriter()
        for contract in django2ars.contracts:
            writer.contracts.add(contract)
        writer.writeTo(self)
#       uncomment to check if result is correct
        print self.text