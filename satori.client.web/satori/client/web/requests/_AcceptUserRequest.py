﻿# vim:ts=4:sts=4:sw=4:expandtab
from satori.client.web.URLDictionary import *
from satori.client.web.queries import *
from django.db import models
from satori.client.common import want_import
want_import(globals(), '*')
from _Request import Request

class AcceptUserRequest(Request):
    pathName = 'accept'
    @classmethod
    def process(cls, request):
        cu = Contestant.filter({'id':int(request.POST['conuser_id'])})[0]
        if 'revoke' in  request.POST.keys():
            status = False
        else:
            status = True
        cu.accepted = status
        d = ParseURL(request.POST['back_to'])
        return GetLink(d,'')
