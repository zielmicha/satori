from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from satori.client.common.remote import *
from URLDictionary import *
from satori.client.web.widgets import Widget
from requests import process
from getfile import *
from queries import DefaultLayout
                
def load(request,argstr,path = ""):
	Session.request = request
	try:
            token_container.set_token(request.COOKIES.get('satori_token', ''))
        except:
            token_container.set_token('')
	params = ParseURL(argstr)
	try:
            w = Widget.FromDictionary(params,path)
            res = render_to_response(w.htmlFile, {'widget' : w} )
        except (TokenInvalid, TokenExpired):
            token_container.set_token('')
	    link = GetLink(DefaultLayout(dict=params,maincontent='loginform'),path)
	    res = HttpResponseRedirect(link)
	    res.set_cookie('satori_token', '')
	    return res
	if request.COOKIES.get('satori_token', '') != token_container.get_token():
	    res.set_cookie('satori_token', token_container.get_token())
	return res

def loadPOST(request,argstr=""):
	Session.request = request
        try:
            token_container.set_token(request.COOKIES.get('satori_token', ''))
        except:
            token_container.set_token('')
        try:
            res = process(argstr,request)
        except (TokenInvalid, TokenExpired):
            link = GetLink(DefaultLayout(dict=params,maincontent='loginform'),path)
            res = HttpResponseRedirect(link)
            res.set_cookie('satori_token', '')
            return res
	if request.COOKIES.get('satori_token', '') != token_container.get_token():
	    res.set_cookie('satori_token', token_container.get_token())
	return res

def loadfile(request,argstr=""):
	Session.request = request
	try:
            token_container.set_token(request.COOKIES.get('satori_token', ''))
        except:
            token_container.set_token('')
        try:
            res = getfile(argstr,request)
        except (TokenInvalid, TokenExpired):
            link = GetLink(DefaultLayout(dict=params,maincontent='loginform'),path)
            res = HttpResponseRedirect(link)
            res.set_cookie('satori_token', '')
            return res
	if request.COOKIES.get('satori_token', '') != token_container.get_token():
	    res.set_cookie('satori_token', token_container.get_token())
	return res
