﻿
from URLDictionary import *
from satori.client.common import want_import
want_import(globals(), '*')
from datetime import datetime
from xml.dom import minidom
from satori.client.web.sphinx.translator import rendertask
from satori.client.web.urls import PROJECT_PATH
import os


# Module for database queries


def UserById(uid):
	return User(int(uid))

def ContestById(cid):
	return Contest.filter({'id' : int(cid)})[0]

def CurrentUser():
    return Security.whoami_user()

def ActiveContest(d):
	if not 'contestid' in d.keys():
		return None
	try:
        	return ContestById(int(d['contestid'][0]))
        except:
                return None

def MyContestant(c,u = None):
    if not u:
        u = CurrentUser()
    if u and c:
	try:
	    cu =c.find_contestant(user = u)
	except:
	    return None
	else:
	    return cu
    else:
	return None
	

def CurrentContestant(d):
	return MyContestant(ActiveContest(d))

def Allowed(o, str):
    if o=='global':
        return Privilege.global_demand(str)
    return Privilege.demand(o, str)

#def explicit_right(object,role,right,moment=datetime.now()):
#    for p in Privilege.filter({'role':role, 'object':object, 'right':right}):
#        if not moment:
#            return True
#        if (not p.startOn or p.StartOn<datetime.now()) and (not p.finishOn or p.finishOn>datetime.now()):
#            return True
#    return False

# default dictionary, if need to return to main screen
def DefaultLayout(dict = {}, maincontent = 'news', contest = None, **kwargs):
        if not contest:
    	    contest = ActiveContest(dict)
	params = kwargs
	params['name'] = [maincontent]
	d = {'name' : ['cover'], 
         'cover' :[{'name' : ['main'], 
                    'content' : [params], 
                    #'loginspace' : [{'name' : ['loginform']}],
                    'headerspace' : [{'name': ['header']}]
                  }]
        }
	#d = {'name' : ['main'], 'content' : [{'name' : ['news']} ], 'login' : [{'name' : ['login']}]}
	if contest:
		d['contestid'] = [str(contest.id)]
	return d


def text2html(text):
    return rendertask(unicode(text), os.path.join(PROJECT_PATH, 'files'), 'files')
    

def parse_judge(judge_content):
    ret = []
    xml = ''
    for line in judge_content.splitlines(True):
        if line[0:2]=="#@":
            xml = xml+line.strip("#@")
    tree = minidom.parseString(xml)
    idata = tree.getElementsByTagName("input")[0]
    for n in idata.childNodes:
        if n.nodeName=="value" or n.nodeName=="file":
            d = {}
            d["type"] = n.nodeName
            d["name"] = n.getAttribute("name")
            d["description"] = n.getAttribute("description")
            d["required"] = n.getAttribute("required")=="true"
            d["default"] = n.getAttribute("default")
            ret.append(d)
    return ret
