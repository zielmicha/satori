# vim:ts=4:sts=4:sw=4:expandtab
from satori.client.common import want_import
want_import(globals(), '*')
from satori.tools import params
from satori.web.utils.decorators import contest_view
from satori.web.utils import xmlparams
from satori.web.utils.shortcuts import text2html
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms


@contest_view
def view(request, page_info, id):
    ranking = Ranking(int(id))
    return render_to_response('ranking.html', {'page_info' : page_info, 'ranking' : ranking, 'content' : text2html(ranking.full_ranking())})


class AddBaseForm(forms.Form):
    ranking_name = forms.CharField(label="Ranking name", required=True)
    ranking_visibility = forms.ChoiceField(label="Ranking visible for", required=True, choices=[['admin','Admins only'],['contestant','Contestants'],['public', 'Everyone']])

@contest_view
def add(request, page_info):
    contest = page_info.contest
    aggregators = Global.get_aggregators()

    class AddSimpleForm(forms.Form):
        selected=forms.ChoiceField(choices=[[a,a] for a in aggregators.keys()],label="Select ranking type")
                
    selected = request.GET.get("selected",None)
    if not selected:
        form = AddSimpleForm()
        return render_to_response('ranking_add.html', {'page_info' : page_info, 'form' : form})
        
    parser = params.parser_from_xml(description=aggregators[selected],section='aggregator',subsection='general')
    if request.method=="POST":
        base_form = AddBaseForm(request.POST)
        form = xmlparams.ParamsForm(parser=parser,data=request.POST)
        if base_form.is_valid() and form.is_valid():
            ranking = Ranking.create(RankingStruct(contest=page_info.contest,name=base_form.cleaned_data["ranking_name"],aggregator=selected,is_public=False),parser.write_oa_map(form.cleaned_data), {}, {})
            newvis = base_form.cleaned_data["ranking_visibility"]
            if newvis=='public':
                Privilege.grant(contest.contestant_role,ranking,'VIEW_FULL')
                Privilege.grant(contest.contestant_role,ranking,'VIEW')
                public = True
            elif newvis=='contestant':
                Privilege.grant(contest.contestant_role,ranking,'VIEW_FULL')
                Privilege.grant(contest.contestant_role,ranking,'VIEW')
                public = False
            else:
                Privilege.revoke(contest.contestant_role,ranking,'VIEW_FULL')
                Privilege.revoke(contest.contestant_role,ranking,'VIEW')
                public = False                    
            ranking.is_public = public
            return HttpResponseRedirect(reverse('ranking_edit',args=[contest.id,ranking.id]))
    else:
        base_form = AddBaseForm()
        form = xmlparams.ParamsForm(parser=parser,initial=parser.read_oa_map({},check_required=False))
    return render_to_response('ranking_add.html', {'page_info' : page_info, 'base_form' : base_form, 'form' : form, 'selected' : selected})


@contest_view
def edit(request, page_info, id):
    aggregators = Global.get_aggregators()
    ranking = Ranking(int(id))
    contest = page_info.contest
    problems = ProblemMapping.filter(ProblemMappingStruct(contest=contest))
    problems.sort(key=lambda p : p.code)
    suites_raw = ranking.get_problem_test_suites()
    params_raw = ranking.get_problem_params()
    suites = dict([[k.id, v] for k, v in suites_raw.iteritems()])
    problem_params = dict([[k.id, v] for k, v in params_raw.iteritems()])
    problem_list = [ [p,suites.get(p.id,None),problem_params.get(p.id,None)] for p in problems ]
    if ranking.is_public:
        visibility = 'public'
    elif Privilege.get(contest.contestant_role,ranking,'VIEW'):
        visibility = 'contestant'
    else:
        visibility = 'admin'        
    parser = params.parser_from_xml(description=aggregators[ranking.aggregator],section='aggregator',subsection='general')
    if request.method=="POST":
        if 'delete' in request.POST.keys():
            ranking.delete()
            return HttpResponseRedirect(reverse('contest_manage',args=[contest.id]))
        base_form = AddBaseForm(request.POST)
        form = xmlparams.ParamsForm(parser=parser,data=request.POST)
        if base_form.is_valid() and form.is_valid():
            newvis = base_form.cleaned_data["ranking_visibility"]
            public = ranking.is_public
            if newvis != visibility:
                if newvis=='public':
                    Privilege.grant(contest.contestant_role,ranking,'VIEW_FULL')
                    Privilege.grant(contest.contestant_role,ranking,'VIEW')
                    public = True
                elif newvis=='contestant':
                    Privilege.grant(contest.contestant_role,ranking,'VIEW_FULL')
                    Privilege.grant(contest.contestant_role,ranking,'VIEW')
                    public = False
                else:
                    Privilege.revoke(contest.contestant_role,ranking,'VIEW_FULL')
                    Privilege.revoke(contest.contestant_role,ranking,'VIEW')
                    public = False                    
            ranking.modify_full(RankingStruct(contest=page_info.contest,name=base_form.cleaned_data["ranking_name"],aggregator=ranking.aggregator,is_public=public),parser.write_oa_map(form.cleaned_data), suites_raw, params_raw)
            return HttpResponseRedirect(reverse('ranking_edit',args=[contest.id,id]))
    else:
        base_form = AddBaseForm(initial={'ranking_name' : ranking.name, 'ranking_visibility' : visibility})
        form = xmlparams.ParamsForm(parser=parser,initial=parser.read_oa_map(ranking.params_get_map(),check_required=False))
    return render_to_response('ranking_edit.html', {'page_info' : page_info, 'ranking' : ranking, 'base_form' : base_form, 'form' : form, 'problem_list' : problem_list})



@contest_view
def editparams(request, page_info, id, problem_id):
    aggregators = Global.get_aggregators()
    ranking = Ranking(int(id))
    contest = page_info.contest
    problem = ProblemMapping(int(problem_id))
    allparams = ranking.get_problem_params()
    allsuites = ranking.get_problem_test_suites()
    problem_params = {}
    for k, v in allparams.iteritems():
        if k.id==int(problem_id):
            problem_params = v
    current_suite = None
    for k, v in allsuites.iteritems():
        if k.id==int(problem_id):
            current_suite = v
    
    class ParamsBaseForm(forms.Form):
        suite = forms.ChoiceField(choices=[[0,'Use default']]+[[s.id,s.name] for s in TestSuite.filter(TestSuiteStruct(problem=problem.problem))],label='Test suite')
    suiteid=0
    if current_suite:
        suiteid = current_suite.id
    parser = params.parser_from_xml(description=aggregators[ranking.aggregator],section='aggregator',subsection='problem')
    if request.method=="POST":
        if 'erase' in request.POST.keys():
            ranking.modify_problem(problem=problem,test_suite=None,params={})
            ranking.rejudge()
            return HttpResponseRedirect(reverse('ranking_edit',args=[page_info.contest.id,ranking.id]))
        base_form = ParamsBaseForm(data=request.POST)
        form = xmlparams.ParamsForm(parser=parser,data=request.POST)
        if base_form.is_valid() and form.is_valid():            
            data = base_form.cleaned_data
            if int(base_form.cleaned_data['suite'])==0:
                newsuite = None
            else:
                newsuite = TestSuite(int(base_form.cleaned_data['suite']))
#            ranking.set_problem_test_suites({problem : newsuite})
#            ranking.set_problem_params({problem : parser.write_oa_map(form.cleaned_data)})
            ranking.modify_problem(problem=problem,test_suite=newsuite,params=parser.write_oa_map(form.cleaned_data))
            ranking.rejudge()
            return HttpResponseRedirect(reverse('ranking_edit',args=[page_info.contest.id,ranking.id]))
    else:
        base_form = ParamsBaseForm(initial={'suite' : suiteid})
        form = xmlparams.ParamsForm(parser=parser,initial=parser.read_oa_map(problem_params,check_required=False))
    return render_to_response('ranking_editparams.html', {'page_info' : page_info, 'ranking' : ranking, 'form' : form, 'base_form' : base_form})
    
@contest_view
def rejudge(request, page_info, id):
    ranking = Ranking(int(id))
    ranking.rejudge()
    return HttpResponseRedirect(reverse('contest_manage',args=[page_info.contest.id]))