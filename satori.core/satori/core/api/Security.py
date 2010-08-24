# vim:ts=4:sts=4:sw=4:expandtab
"""
Security and authorization procedures.
"""

from datetime import datetime, timedelta
from types import NoneType
import string
import random
import urlparse
import urllib

from openid.consumer import consumer
from openid.extensions import sreg as oidsreg
from openid.extensions import pape as oidpape
from openid.extensions import ax as oidax

from satori.core.sec.tools import RightCheck, RoleSet, Token
from satori.core.sec.store import Store

from satori.objects import DispatchOn, Argument, ReturnValue
from satori.core.models import Object, User, Login, OpenIdentity, Global, Role
from satori.ars.wrapper import Struct, StaticWrapper, TypedMap

def openid_salt():
    chars = string.letters + string.digits
    salt = ''
    for i in range(16):
        salt += random.choice(chars)
    return salt

OpenIdRedirect = Struct('OpenIdRedirect', (
    ('token', Token, False),
    ('redirect', str, True),
    ('html', str, True)
))

security = StaticWrapper('Security')

@security.method
@ReturnValue(type=Role)
def anonymous():
    globe = Global.get_instance()
    return globe.anonymous

@security.method
@ReturnValue(type=Role)
def authenticated():
    globe = Global.get_instance()
    return globe.authenticated

@security.method
@Argument('token', type=Token)
@ReturnValue(type=User)
def whoami(token):
    if not token.valid:
        raise Exception("Provided token is invalid.")
    return token.user

@security.method
@Argument('token', type=Token)
@Argument('object', type=Object)
@Argument('right', type=str)
@ReturnValue(type=bool)
def right_have(token, object, right):
    checker = RightCheck()
    roleset = RoleSet(token=token)
    return checker(roleset, object, right)

@security.method
@Argument('login', type=str)
@Argument('namespace', type=str, default='')
@ReturnValue(type=bool)
def login_free(login, namespace):
    return len(Login.objects.filter(namespace=namespace, login=login)) == 0

@security.method
@Argument('login', type=str)
@Argument('password', type=str)
@Argument('fullname', type=str)
@ReturnValue(type=User)
def register(login, password, fullname):
    user = User(login=login, fullname=fullname)
    user.save()
    auth = Login(login=login, user=user)
    auth.set_password(password)
    auth.save()
    return user

@security.method
@Argument('login', type=str)
@Argument('password', type=str)
@Argument('namespace', type=str, default='')
@ReturnValue(type=Token)
def login(login, password, namespace):
    login = Login.objects.get(namespace=namespace, login=login)
    if login.check_password(password):
        auth = 'login'
        if namespace != '':
            auth = auth + '.' + namespace
    	return Token(user=login.user, auth=auth, validity=timedelta(hours=6))

@security.method
@Argument('login', type=str)
@Argument('old', type=str)
@Argument('new', type=str)
@Argument('namespace', type=str, default='')
@ReturnValue(type=Token)
def passwd(login, old, new, namespace):
    login = Login.objects.get(namespace=namespace, login=login)
    if login.change_password(old, new):
        auth = 'login'
        if namespace != '':
            auth = auth + '.' + namespace
    	return Token(user=login.user, auth=auth, validity=timedelta(hours=6))

def openid_realm(url):
    callback = urlparse.urlparse(url)
    return urlparse.urlunparse((callback.scheme, callback.netloc, '', '', '', ''))

def openid_modify_callback(url, salt):
    callback = urlparse.urlparse(url)
    qs = urlparse.parse_qs(callback.query)
    qs['satori.openid.salt'] = (salt,)
    query = []
    for key, vlist in qs.items():
        for value in vlist:
        	query.append((key,value))
    query = urllib.urlencode(query)
    return urlparse.urlunparse((callback.scheme, callback.netloc, callback.path, callback.params, query, callback.fragment))

def openid_check_callback(url, salt):
    callback = urlparse.urlparse(url)
    qs = urlparse.parse_qs(callback.query)
    if 'satori.openid.salt' not in qs:
        return False
    if len(qs['satori.openid.salt']) != 1:
        return False
    return qs['satori.openid.salt'][0] == salt

def openid_add_ax(request):
    axr = oidax.FetchRequest()
    axr.add(oidax.AttrInfo('http://axschema.org/contact/country/home', 1, True, 'country'))
    axr.add(oidax.AttrInfo('http://axschema.org/contact/email', 1, True, 'email'))
    axr.add(oidax.AttrInfo('http://axschema.org/namePerson/first', 1, True, 'firstname'))
    axr.add(oidax.AttrInfo('http://axschema.org/namePerson/last', 1, True, 'lastname'))
    axr.add(oidax.AttrInfo('http://axschema.org/pref/language', 1, True, 'language'))
    request.addExtension(axr)

def openid_get_ax(response, identity, update =False):
    try:
        axr = oidax.FetchResponse.fromSuccessResponse(response)
        identity.country = axr.getSingle('http://axschema.org/contact/country/home', identity.country)
        identity.email = axr.getSingle('http://axschema.org/contact/email', identity.email)
        identity.language = axr.getSingle('http://axschema.org/pref/language', identity.language)
        firstname = axr.getSingle('http://axschema.org/namePerson/first', None)
        lastname = axr.getSingle('http://axschema.org/namePerson/last', None)
        if firstname != None and lastname != None:
            identity.name = firstname + ' ' + lastname
        identity.save()
        if update:
            user = identity.user
            user.fullname = identity.name
            user.save()
    except:
        pass

def openid_generic_start(openid, return_to, user_id ='', valid =1, ax =False):
    salt = openid_salt()
    session = { 'satori.openid.salt' : salt }
    store = Store()
    request = consumer.Consumer(session, store).begin(openid)
    if ax:
        openid_add_ax(request)
    redirect = ''
    html = ''
    realm = openid_realm(return_to)
    callback = openid_modify_callback(return_to, salt)
    if request.shouldSendRedirect():
        redirect = request.redirectURL(realm, callback)
    else:
        form = request.formMarkup(realm, callback, False, {'id': 'satori_openid_form'})
        html = '<html><body onload="document.getElementById(\'satori_openid_form\').submit()">' + form + '</body></html>'
    token = Token(user_id=user_id, auth='openid', data=session, validity=timedelta(hours=valid)) 
    return {
        'token' : token,
        'redirect' : redirect,
        'html' : html
    }

def openid_generic_finish(token, args, return_to, user =None):
    if not token.valid:
        raise Exception("Provided token is invalid.")
    if token.auth != 'openid':
        return token
    session = token.data
    store = Store()
    response = consumer.Consumer(session, store).complete(args, return_to)
    if response.status != consumer.SUCCESS:
        raise Exception("OpenID failed.")
    callback = response.getReturnTo()
    if not openid_check_callback(callback, session['satori.openid.salt']):
        raise Exception("OpenID failed.")
    if user:
        identity = OpenIdentity(identity=response.identity_url, user=user)
        identity.save()
    else:
        identity = OpenIdentity.objects.get(identity=response.identity_url)
    openid_get_ax(response, identity, update=True)
    token = Token(user=identity.user, auth='openid', validity=timedelta(hours=6)) 
    return token

@security.method
@Argument('openid', type=str)
@Argument('return_to', type=str)
@ReturnValue(type=OpenIdRedirect)
def openid_login_start(openid, return_to):
    return openid_generic_start(openid=openid, return_to=return_to, user_id='', ax=True)

@security.method
@Argument('token', type=Token)
@Argument('args', type=TypedMap(str, str))
@Argument('return_to', type=str)
@ReturnValue(type=Token)
def openid_login_finish(token, args, return_to):
    return openid_generic_finish(token, args, return_to)

@security.method
@Argument('login', type=str)
@Argument('openid', type=str)
@Argument('return_to', type=str)
@ReturnValue(type=OpenIdRedirect)
def openid_register_start(login, openid, return_to):
    return openid_generic_start(openid=openid, return_to=return_to, user_id='', ax=True)
    user = User(login=login, fullname='')
    user.save()
    session = res['token'].data
    session['satori.openid.user'] = user.id
    res['token'].data = session
    return res

@security.method
@Argument('token', type=Token)
@Argument('args', type=TypedMap(str, str))
@Argument('return_to', type=str)
@ReturnValue(type=Token)
def openid_register_finish(token, args, return_to):
    session = token.data
    user = User.objects.get(id=session['satori.openid.user'])
    res = openid_generic_finish(token, args, return_to, user)
    return res

@security.method
@Argument('login', type=str)
@Argument('password', type=str)
@Argument('namespace', type=str, default='')
@Argument('openid', type=str)
@Argument('return_to', type=str)
@ReturnValue(type=OpenIdRedirect)
def openid_add_start(login, openid, return_to):
    login = Login.objects.get(namespace=namespace, login=login)
    if login.check_password(password):
        res = openid_generic_start(openid=openid, return_to=return_to, user_id=str(token.user.id), ax=True)
        session = res['token'].data
        session['satori.openid.user'] = token.user.id
        res['token'].data = session
        return res
    raise Exception("Authorization failed.")

@security.method
@Argument('token', type=Token)
@Argument('args', type=TypedMap(str, str))
@Argument('return_to', type=str)
@ReturnValue(type=Token)
def openid_add_finish(token, args, return_to):
    session = token.data
    user = User.objects.get(id=session['satori.openid.user'])
    res = openid_generic_finish(token, args, return_to, user)
    return res



security._fill_module(__name__)

