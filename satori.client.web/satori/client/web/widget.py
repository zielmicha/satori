﻿from copy import deepcopy
from URLDictionary import *
from queries import *
from satori.core.models import *

allwidgets = {}

class Widget:
    def __init(self,params,path):
        pass

# returns a newly created widget of a given kind
    @staticmethod
    def FromDictionary(dict,path):
        if not ('name' in dict.keys()):
            dict = DefaultLayout(dict)
        d = follow(dict,path)
        name = d['name'][0]
        return allwidgets[name](dict,path)


# login box
class LoginWidget(Widget):
    def __init__(self, params, path):
        el = CurrentUser()
        if el:
            self.htmlFile = 'htmls/logged.html'
            self.name = el.fullname
        else:
            self.htmlFile = 'htmls/loginform.html'
            self.back_to = ToString(params)

# left menu
class MenuWidget(Widget):
    def __init__(self, params, path):
        self.htmlFile = 'htmls/menu.html'
        self.menuitems = []
        contest = ActiveContest(params)
        user = CurrentUser()
        cuser = CurrentContestant(params)

        def addwidget(check,label,wname,object = None,rights = ''):
            if not check:
                return
            if object and not Allowed(object,rights):
                return
            d = DefaultLayout(params)
            f = { 'name' : [wname] };
            d['content'] = [f];
            self.menuitems.append([label,GetLink(d,'')])

        def addlink(check,label,dict,object = None,rights=''):
            if not check:
                return
            if object and not Allowed(object,rights):
                return
            self.menuitems.append([label,GetLink(dict,'')])

        addwidget(True, 'News', 'news')
        addwidget(not contest,'Select contest','selectcontest')
        addwidget(contest,'Problems','problems',contest,'seeproblems')
        addwidget(cuser,'Submit','submit',contest,'submit')
        addwidget(contest,'Results','results',contest,'seeresults')
        addwidget(contest,'Ranking','ranking',contest,'seeranking')
        addwidget(cuser,'Manage contest','mancontest',contest,'manage')
        addwidget(contest,'Manage users','manusers',contest,'manage_users')
        addlink(contest,'Main screen',DefaultLayout())

# news table (a possible main content)
class NewsWidget(Widget):
    def __init__(self, params, path):
        self.htmlFile = 'htmls/news.html'


# results table (a possible main content)
class ResultsWidget(Widget):
    def __init__(self, params, path):
        self.htmlFile = 'htmls/results.html'
        c = ActiveContest(params)
        _params = deepcopy(params)
        d = follow(_params,path)
        if not ('shown' in d.keys()):
            shown = []
        else:
            shown = d['shown']
        self.submits = []
        for o in Submit.objects.filter(owner__contest=c):
            s = {}
            id = str(o.id)
            s["id"] = id
            s["time"] = o.time
            s["user"] = o.owner.user.fullname
            s["problem"] = o.problem.code
            s["status"] = o.shortstatus
            s["details"] = o.longstatus
            _shown = deepcopy(shown)
            if id in _shown:
                s["showdetails"] = True
                _shown.remove(id)
            else:
                s["showdetails"] = False
                _shown.append(id)
            _shown.sort()
            d['shown'] = _shown
            if _shown == []:
                del d['shown']
            s["link"] = GetLink(_params,'')
            self.submits.append(s)

# ranking (a possible main content)
class RankingWidget(Widget):
    def __init__(self, params, path):
        self.htmlFile = 'htmls/ranking.html'


class SubmitWidget(Widget):
    def __init__(self, params, path):
        self.htmlFile = 'htmls/submit.html'
        self.back_to = ToString(params)
        c = ActiveContest(params)
        self.problems = []
        self.cid = CurrentContestant(params).id
        for p in ProblemMapping.objects.filter(contest=c):
            if Allowed(p,'submit'):
                self.problems.append(p)

class ManageUsersWidget(Widget):
    def __init__(self, params, path):
        self.htmlFile = 'htmls/manusers.html'
        c = ActiveContest(params)
        self.accepted = Contestant.objects.filter(contest=c,accepted=True)
        self.pending = Contestant.objects.filter(contest=c,accepted=False)

class ManageContestWidget(Widget):
    def __init__(self, params, path):
        self.htmlFile = 'htmls/mancontest.html'

class ProblemsWidget(Widget):
    def __init__(self, params, path):
        self.htmlFile = 'htmls/problems.html'
        c = ActiveContest(params)
        self.problems = ProblemMapping.objects.filter(contest=c)

# contest selection screen (a possible main content)
class SelectContestWidget(Widget):
    def __init__(self, params, path):
        self.htmlFile = 'htmls/selectcontest.html'
        self.participating = []
        self.mayjoin = []
        self.other = []
        self.user = CurrentUser()
        for c in Contest.objects.all():
            cu = MyContestant(c)
            d = DefaultLayout()
            d['contestid'] = [str(c.id)]
            if cu and cu.accepted:
                self.participating.append([c,cu,GetLink(d,'')])
            elif c.joining == 'Public' or c.joining == 'Moderated':
                self.mayjoin.append([c,cu,GetLink(d,'')])
            else:
                self.other.append([c,cu,GetLink(d,'')])

# base widget
class MainWidget(Widget):
    def __init__(self, params, path):
        self.htmlFile = 'htmls/index.html'
        self.loginform = LoginWidget(params,path)
        self.menu = MenuWidget(params,path)
        if not ('content' in params.keys()):
            params['content'] = [{'name' : ['news']}]
        self.content = Widget.FromDictionary(params,'content');
        self.params = params


allwidgets = {
'main' : MainWidget, 
'menu' : MenuWidget, 'news' : NewsWidget, 
'selectcontest' : SelectContestWidget, 
'loginform' : LoginWidget, 
'ranking' : RankingWidget, 
'results' : ResultsWidget, 
'submit' : SubmitWidget,
'manusers' : ManageUsersWidget,
'mancontest' : ManageContestWidget,
'problems' : ProblemsWidget
}
