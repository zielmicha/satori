# vim:ts=4:sts=4:sw=4:expandtab
from satori.client.common import want_import
want_import(globals(), '*')
from satori.web.utils.decorators import contest_view
from django import forms
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

@contest_view
def view(request, page_info):
    contest = page_info.contest
    submitable = [["",'Select a problem']]
    problems = ProblemMapping.filter(ProblemMappingStruct(contest=contest))
    problems.sort(key=lambda p: p.code)
    for problem in problems:
        if Privilege.demand(problem,"SUBMIT"):
            submitable.append((problem.id, problem.code+": "+problem.title))
    class SubmitForm(forms.Form):
        problem = forms.ChoiceField(submitable,label='Please select problem')
#        code = forms.CharField(required=False,widget=forms.Textarea, label='Paste code')
        codefile = forms.FileField(required=False, label='Upload file')
        
        def clean(self):
            data = self.cleaned_data
#            if data["code"]=="" and not data["codefile"]:
            if not data["codefile"]:
                raise forms.ValidationError("No code given!")
            return data
            
    if request.method == "POST":
        form = SubmitForm(request.POST,request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            pid = int(data["problem"])
            problem = ProblemMapping.filter(ProblemMappingStruct(id=pid))[0]
#            if data["code"]!="":
#                content = data["code"]
#                filename = problem.code
            if data["codefile"]:
                content = data["codefile"].read()
                filename = data["codefile"].name
            Submit.create(SubmitStruct(problem=problem),content=content,filename=filename)
            return HttpResponseRedirect(reverse('results',args=[page_info.contest.id]))
    else:
        form = SubmitForm(initial={'problem' : request.GET.get('select',None)})
    return render_to_response('submit.html', {'page_info' : page_info, 'form' : form})
