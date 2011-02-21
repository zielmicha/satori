# vim:ts=4:sts=4:sw=4:expandtab
from django.conf.urls.defaults import *
from django.conf import settings

from satori.client.common import remote
remote.setup(settings.THRIFT_HOST, settings.THRIFT_PORT, settings.BLOB_PORT)

import os
PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

# Please keep the urlpatterns sorted.

contestadminpatterns = patterns('',
    (r'$', 'satori.web.views.contest.admin.manage.view'),
    (r'contestants$', 'satori.web.views.contest.admin.contestants.view'),
    (r'news/(?P<id>\d+)$', 'satori.web.views.contest.admin.news.view'),
    (r'questions$', 'satori.web.views.contest.contest.admin.questions.view'),
    (r'questions/(?P<id>\d+)$', 'satori.web.views.contest.admin.editquestion.view'),
    (r'ranking/(?P<id>\d+)$', 'satori.web.views.contest.admin.ranking.view'),
    (r'subpage/(?P<id>\d+)$', 'satori.web.views.contest.admin.subpage.view'),
)

contestpatterns = patterns('',
    url(r'^$', 'satori.web.views.contest.news.view', name='contest_main'),
    url(r'news$', 'satori.web.views.contest.news.view', name='contest_news'),
    url(r'news/create$', 'satori.web.views.contest.news.create', name='contest_news_create'),
    url(r'news/(?P<id>\d+)/edit$', 'satori.web.views.contest.news.edit', name='contest_news_edit'),
    url(r'news/(?P<id>\d+)/delete$', 'satori.web.views.contest.news.delete', name='contest_news_delete'),
    url(r'print', 'satori.web.views.contest.print.view', name='print'),
    url(r'problems$', 'satori.web.views.contest.problems.view', name='contest_problems'),
    url(r'problems/(?P<id>\d+)$', 'satori.web.views.contest.viewproblem.view', name='contest_view_problem'),
    url(r'questions$', 'satori.web.views.contest.questions.view', name='questions'),
    url(r'answers$', 'satori.web.views.contest.answers.view', name='answers'),
    url(r'ranking/(?P<id>\d+)$', 'satori.web.views.contest.ranking.view', name='ranking'),
    url(r'results$', 'satori.web.views.contest.results.view', name='results'),
    url(r'results/(?P<id>\d+)$', 'satori.web.views.contest.viewresult.view', name='view_result'),
    url(r'submit$', 'satori.web.views.contest.submit.view', name='submit'),
    url(r'subpage/create$', 'satori.web.views.contest.subpage.create', name='contest_subpage_create'),
    url(r'subpage/(?P<id>\d+)$', 'satori.web.views.contest.subpage.view', name='contest_subpage'),
    url(r'subpage/(?P<id>\d+)/edit$', 'satori.web.views.contest.subpage.edit', name='contest_subpage_edit'),
    url(r'subpage/(?P<id>\d+)/delete$', 'satori.web.views.contest.subpage.delete', name='contest_subpage_delete'),

#    (r'^admin/', include(contestadminpatterns)),
)

adminpatterns = patterns('',
    url(r'news/(?P<id>\d+)$', 'satori.web.views.admin.news.view', name='edit_news'),
    url(r'problems$', 'satori.web.views.admin.problems.view', name='problem_repository'),
    url(r'problems/(?P<id>\d+)$', 'satori.web.views.admin.viewproblem.view', name='edit_problem'),
    url(r'ranking/(?P<id>\d+)$', 'satori.web.views.admin.ranking.view'),
    url(r'subpages/(?P<id>\d+)$', 'satori.web.views.admin.subpages.view', name='edit_subpage'),
    url(r'users$', 'satori.web.views.admin.users.view', name='users'),
    url(r'users/(?P<id>\d+)$', 'satori.web.views.admin.edituser.view', name='edit_user'),
)

urlpatterns = patterns('',
    (r'^$', 'satori.web.views.news.view'),
    url(r'^news$', 'satori.web.views.news.view', name='news'),
    url(r'^news/create$', 'satori.web.views.news.create', name='news_create'),
    url(r'^news/(?P<id>\d+)/edit$', 'satori.web.views.news.edit', name='news_edit'),
    url(r'^news/(?P<id>\d+)/delete$', 'satori.web.views.news.delete', name='news_delete'),
    url(r'^contest/select$', 'satori.web.views.select.view', name='select_contest'),
    url(r'^login$', 'satori.web.views.login.view', name='login'),
    url(r'^logout$', 'satori.web.views.logout.view', name='logout'),
    url(r'^news$', 'satori.web.views.news.view', name='news'),
    url(r'^profile$', 'satori.web.views.profile.view', name='profile'),
    url(r'^register$', 'satori.web.views.register.view', name='register'),
    url(r'^subpage/(?P<id>\d+)$', 'satori.web.views.subpage.view', name='subpage'),

#    (r'admin/', include(adminpatterns)),
    (r'contest/(?P<contestid>\d+)/', include(contestpatterns)),

    (r'^files/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(PROJECT_PATH,'files')}),
)
