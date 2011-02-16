# vim:ts=4:sts=4:sw=4:expandtab
from satori.client.common import want_import
want_import(globals(), '*')
from satori.web.utils.decorators import general_view
from satori.web.utils.shortcuts import text2html
from django.shortcuts import render_to_response

@general_view
def view(request, general_page_overview):
    messages = []
    for message in Subpage.get_global(True):
        messages.append([message,text2html(message.content)])
    return render_to_response('news.html',{'general_page_overview' : general_page_overview, 'messages' : messages })
