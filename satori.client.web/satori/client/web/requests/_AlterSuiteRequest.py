# vim:ts=4:sts=4:sw=4:expandtab
from satori.client.web.URLDictionary import *
from satori.client.web.queries import *
from django.db import models
from satori.client.common.remote import *
from _Request import Request

class AlterSuiteRequest(Request):
    pathName = 'altersuite'
    @classmethod
    def process(cls, request):
        ts = TestSuite.filter(TestSuiteStruct(id=int(request.POST['id'])))[0]
        tests = []
        for k in request.POST.keys():
            if k[0:4] == 'test':
                t = Test.filter({'id':int(k[4:])})[0]
                tests.append(t)
        name = request.POST['name']
        description = request.POST['description']
        ts.modify_full(TestSuiteStruct(name=name,description=description),tests)
        d = ParseURL(request.POST['back_to'])
        return GetLink(d,'')
