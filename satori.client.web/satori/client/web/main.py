from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from satori.client.common.remote import *
from URLDictionary import *
from satori.client.web.widgets import Widget
from requests import process
                
def load(request,argstr,path = ""):
	Session.request = request
	token_container.set_token(request.COOKIES.get('satori_token', ''))
	params = ParseURL(argstr)
	w = Widget.FromDictionary(params,path)
	res = render_to_response(w.htmlFile, {'widget' : w} )
	if request.COOKIES.get('satori_token', '') != token_container.get_token():
	    res.set_cookie('satori_token', token_container.get_token())
	return res

def loadPOST(request,argstr=""):
	Session.request = request
	token_container.set_token(request.COOKIES.get('satori_token', ''))
	res = process(argstr,request)
	if request.COOKIES.get('satori_token', '') != token_container.get_token():
	    res.set_cookie('satori_token', token_container.get_token())
	return res
