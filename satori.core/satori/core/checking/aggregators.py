# -*- coding: utf-8 -*-
# vim:ts=4:sts=4:sw=4:expandtab
import logging
import yaml
from blist import blist, sortedset, sortedlist
from collections import deque
from copy import deepcopy
from datetime import datetime, timedelta
from operator import attrgetter

from django.db.models import F

from satori.ars import perf
from satori.core.models import Contestant, Test, TestResult, TestSuiteResult, Ranking, RankingEntry, Contest, ProblemMapping, RankingParams
from satori.events import Event, Client2
from satori.core.checking.utils import RestTable
from satori.objects import Namespace
from satori.tools.params import parse_params, total_seconds

maxint = 2*(10**9)

class AggregatorBase(object):
    def __init__(self, supervisor, ranking):
        super(AggregatorBase, self).__init__()
        self.supervisor = supervisor
        self.ranking = ranking

        self.test_suites = {}
        self.problem_cache = {}
        self.submit_cache = {}
        self.scores = {}
        self.params = Namespace()
        self.problem_params = {}

    def init(self):
        self.params = parse_params(self.__doc__, 'aggregator', 'general', self.ranking.params_get_map())

        for rp in RankingParams.objects.filter(ranking=self.ranking):
            self.problem_params[rp.problem_id] = parse_params(self.__doc__, 'aggregator', 'problem', rp.params_get_map())
            if rp.test_suite:
                self.test_suites[rp.problem_id] = rp.test_suite

        for p in ProblemMapping.objects.filter(contest__id=self.ranking.contest_id):
            self.problem_cache[p.id] = p
            if p.id not in self.test_suites:
                self.test_suites[p.id] = p.default_test_suite
            if p.id not in self.problem_params:
                self.problem_params[p.id] = parse_params(self.__doc__, 'aggregator', 'problem', {})

    def position(self):
        return u''

    def changed_contestants(self):
        ranking_entry_cache = dict((r.contestant_id, r) for r in RankingEntry.objects.filter(ranking=self.ranking))

        new_contestants = set()
        old_contestants = set(self.scores.keys())
        for c in Contestant.objects.filter(contest__id=self.ranking.contest_id, accepted=True):
            new_contestants.add(c.id)

            if not c.id in self.scores:
                self.scores[c.id] = self.get_score()

            self.scores[c.id].contestant = c
            self.scores[c.id].hidden = c.invisible and not getattr(self.params, 'show_invisible', False)
            if c.id in ranking_entry_cache:
                self.scores[c.id].ranking_entry = ranking_entry_cache[c.id]
            else:
                (self.scores[c.id].ranking_entry, created) = RankingEntry.objects.get_or_create(ranking=self.ranking, contestant=c, defaults={'position': self.position()})

            self.scores[c.id].update()
    
        for cid in old_contestants:
            if cid not in new_contestants:
                del self.scores[cid]
    
    def created_submits(self, submits):
        for submit in submits:
            self.submit_cache[submit.id] = submit
            self.supervisor.schedule_test_suite_result(self.ranking, submit, self.test_suites[submit.problem_id])
    
    def checked_test_suite_results(self, test_suite_results):
        changed_contestants = set()
        
        for result in test_suite_results:
            s = self.submit_cache[result.submit_id]
            self.scores[s.contestant_id].aggregate(result)
            changed_contestants.add(s.contestant_id)

        for cid in changed_contestants:
            self.scores[cid].update()

    def tick(self):
        pass


class ACMAggregator(AggregatorBase):
    """
#@<aggregator name="ACM style aggregator">
#@      <general>
#@              <param type="bool"     name="show_invisible" description="Show invisible submits" default="false"/>
#@              <param type="bool"     name="show_zero"      description="Hide contestants with zero score" default="true"/>
#@              <param type="datetime" name="time_start"     description="Submission start time"/>
#@              <param type="datetime" name="time_stop"      description="Submission stop time (freeze)"/>
#@              <param type="time"     name="time_penalty"   description="Penalty for wrong submit" default="1200s"/>
#@              <param type="int"      name="max_stars"      description="Maximal number of stars" default="4"/>
#@      </general>
#@      <problem>
#@              <param type="bool"     name="ignore"         description="Ignore problem" default="false"/>
#@              <param type="float"    name="score"          description="Score" default="1"/>
#@              <param type="datetime" name="time_start"     description="Submission start time"/>
#@              <param type="datetime" name="time_stop"      description="Submission stop time (freeze)"/>
#@      </problem>
#@</aggregator>
    """
    def position(self,  score=0, time=maxint, name=''):
        return (u'%09d%09d%s' % (maxint - score, time, name))[0:50]

    class ACMScore(object):
        class ACMProblemScore(object):
            def __init__(self, score, problem):
                self.score = score
                self.ok = False
                self.star_count = 0
                self.ok_time = timedelta()
                self.ok_submit = None
                self.result_list = sortedlist()
                self.problem = problem
                self.params = self.score.aggregator.problem_params[problem.id]

            def aggregate(self, result):
                time = self.score.aggregator.submit_cache[result.submit_id].time
                ok = result.oa_get_str('status') in ['OK', 'ACC']
                if self.params.time_stop and time > self.params.time_stop:
                    return
                if self.params.ignore:
                    return
                if ok:
                    self.ok = True
                self.result_list.add((time, ok, result.submit_id))
                if self.ok:
                    self.star_count = 0
                    for (time, ok, submit_id) in self.result_list:
                        if ok:
                            if self.params.time_start and time > self.params.time_start:
                                self.ok_time = time - self.params.time_start
                            else:
                                self.ok_time = time - datetime.fromtimestamp(0)
                            self.ok_submit = submit_id
                            break
                        self.star_count += 1

            def get_str(self):
                if self.star_count > 0:
                    if self.star_count <= self.score.aggregator.params.max_stars:
                        return self.problem.code + '*' * self.star_count
                    else:
                        return self.problem.code + '\\ :sup:`(' + str(self.star_count) + ')`\\'
                else:
                    return self.problem.code

        def __init__(self, aggregator):
            self.aggregator = aggregator
            self.hidden = False
            self.scores = {}

        def update(self):
            score_list = [s for s in self.scores.values() if s.ok]
            if self.hidden or (not score_list and not self.aggregator.params.show_zero):
                self.ranking_entry.row = ''
                self.ranking_entry.individual = ''
                self.ranking_entry.position = self.aggregator.position()
                self.ranking_entry.save()
            else:
                points = int(sum([s.params.score for s in score_list], 0.0))
                time = sum([s.ok_time + self.aggregator.params.time_penalty * s.star_count for s in score_list], timedelta(0))
                time_seconds = int(total_seconds(time))
                time_str = str(timedelta(seconds=time_seconds))
                problems = ' '.join([s.get_str() for s in sorted([s for s in score_list], key=attrgetter('ok_time'))])

                contestant_name = self.aggregator.table.escape(self.contestant.name)

                self.ranking_entry.row = self.aggregator.table.generate_row('', contestant_name, str(points), time_str, problems) + self.aggregator.table.row_separator
                self.ranking_entry.individual = ''
                self.ranking_entry.position = self.aggregator.position(points, time_seconds, self.contestant.name)
                self.ranking_entry.save()

        def aggregate(self, result):
            submit = self.aggregator.submit_cache[result.submit_id]
            if submit.problem_id not in self.scores:
                self.scores[submit.problem_id] = self.ACMProblemScore(self, self.aggregator.problem_cache[submit.problem_id])
            self.scores[submit.problem_id].aggregate(result)

    def __init__(self, supervisor, ranking):
        super(ACMAggregator, self).__init__(supervisor, ranking)

    def init(self):
        super(ACMAggregator, self).init()
        for pid, params in self.problem_params.iteritems():
            if params.time_start is None:
                params.time_start = self.params.time_start
            if params.time_stop is None:
                params.time_stop = self.params.time_stop

        self.table = RestTable((4, 'Lp.'), (32, 'Name'), (8, 'Score'), (16, 'Time'), (16, 'Tasks'))
        
        self.ranking.header = self.table.row_separator + self.table.header_row + self.table.header_separator
        self.ranking.footer = self.table.header_row + self.table.row_separator
        self.ranking.save()
        
    def get_score(self):
        return self.ACMScore(self)


class PointsAggregator(AggregatorBase):
    """
#@<aggregator name="Points aggregator">
#@      <general>
#@      </general>
#@      <problem>
#@      </problem>
#@</aggregator>
    """
    def position(self,  score=0, name=''):
        return (u'%09d%s' % (maxint - score, name))[0:50]
    class PointsScore(object):
        class PointsProblemScore(object):
            def __init__(self, score, problem):
                self.score = score
                self.points = None
                self.last_time = datetime.min
                self.problem = problem

            def aggregate(self, result):
                checked = int(result.oa_get_str('checked'))
                passed = int(result.oa_get_str('passed'))
                if checked == 0:
                    points = 0
                else:
                    points = int(100*passed/checked)
                if self.score.aggregator.submit_cache[result.submit_id].time > self.last_time:
                    self.points = points

        def __init__(self, aggregator):
            self.aggregator = aggregator
            self.hidden = False
            self.scores = {}
            for problem_id in self.aggregator.problem_cache:
                self.scores[problem_id] = self.PointsProblemScore(self, self.aggregator.problem_cache[problem_id])

        def update(self):
            if self.hidden or not any([s.points is not None for s in self.scores.values()]):
                self.ranking_entry.row = ''
                self.ranking_entry.individual = ''
                self.ranking_entry.position = self.aggregator.position()
                self.ranking_entry.save()
            else:
                points = sum([s.points for s in self.scores.values() if s.points is not None], 0.0)
                
                contestant_name = self.aggregator.table.escape(self.contestant.name)
        
                row = ['', contestant_name]
                for problem in self.aggregator.problem_list:
                    if self.scores[problem.id].points is not None:
                        row.append(self.scores[problem.id].points)
                    else:
                        row.append('\-')
                row.append(points)

                self.ranking_entry.row = self.aggregator.table.generate_row(*row) + self.aggregator.table.row_separator
                self.ranking_entry.individual = ''
                self.ranking_entry.position = self.aggregator.position(points, self.contestant.name)
                self.ranking_entry.save()

        def aggregate(self, result):
            submit = self.aggregator.submit_cache[result.submit_id]
            self.scores[submit.problem_id].aggregate(result)

    def __init__(self, supervisor, ranking):
        super(PointsAggregator, self).__init__(supervisor, ranking)

    def init(self):
        super(PointsAggregator, self).init()

        self.problem_list = sorted(self.problem_cache.values(), key=attrgetter('code'))
       
        columns = [(5, 'Lp.'), (20, 'Name')]

        for problem in self.problem_list:
            columns.append((10, problem.code))

        columns.append((10, 'Sum'))

        self.table = RestTable(*columns)
        
        self.ranking.header = self.table.row_separator + self.table.header_row + self.table.header_separator
        self.ranking.footer = ''
        self.ranking.save()

    def get_score(self):
        return self.PointsScore(self)

class MarksAggregator(AggregatorBase):
    """
#@<aggregator name="Marks aggregator">
#@      <general>
#@              <param type="bool"     name="show_invisible" description="Show invisible submits" default="false"/>
#@              <param type="float"    name="max_score"      description="Maximum score for each problem" default="1"/>
#@              <param type="float"    name="min_score"      description="Minimum score for each problem" default="-1"/>
#@              <param type="datetime" name="time_start"     description="Submission start time"/>
#@              <param type="datetime" name="time_stop"      description="Ignore submits after"/>
#@              <param type="int"      name="max_stars"      description="Maximal number of stars" default="4"/>
#@              <param type="text"     name="group_points"   description="Number of points for each problem group"/>
#@              <param type="text"     name="points_mark"    description="Marks for points ranges"/>
#@              <param type="bool"     name="show_marks"     description="Show marks" default="true"/>
#@              <param type="bool"     name="show_max_score" description="Show maximum possible score" default="false"/>
#@              <param type="datetime" name="time_start_descent"       description="Descent start time"/>
#@              <param type="time"     name="time_descent"   description="Descent to zero time"/>
#@      </general>
#@      <problem>
#@              <param type="bool"     name="ignore"         description="Ignore problem" default="false"/>
#@              <param type="bool"     name="show"           description="Show column for this problem" default="true"/>
#@              <param type="bool"     name="show_max_score" description="Show maximum possible score"/>
#@              <param type="bool"     name="obligatory"     description="Problem is obligatory" default="1"/>
#@              <param type="float"    name="max_score"      description="Maximum score for problem" default="1"/>
#@              <param type="float"    name="min_score"      description="Minimum score for problem" default="-1"/>
#@              <param type="datetime" name="time_start"     description="Submission start time"/>
#@              <param type="datetime" name="time_stop"      description="Ignore submits after"/>
#@              <param type="datetime" name="time_start_descent"       description="Descent start time"/>
#@              <param type="time"     name="time_descent"   description="Descent to zero time"/>
#@      </problem>
#@</aggregator>
    """
    def position(self,  name=''):
        return (u'%s' % (name))[0:50]

    class MarksScore(object):
        def __init__(self, aggregator):
            self.aggregator = aggregator
            self.hidden = False
            self.scores = {}

        def timed_score(self, score, time, start_descent, descent):
            if time <= start_descent:
                return score
            dif = total_seconds(time - start_descent)
            des = total_seconds(descent)
            if des <= 0:
                return score
            return (1.0 - dif/des) * score

        def update(self):
            if self.hidden:
                self.ranking_entry.row = ''
                self.ranking_entry.individual = ''
                self.ranking_entry.position = self.aggregator.position()
                self.ranking_entry.save()
            else:
                all_ok = True
                points = []
                mpoints = []
                for pid in self.aggregator.sorted_problems:
                    problem = self.aggregator.problem_cache[pid]
                    g_score = self.aggregator.group_score[problem.group]
                    params = self.aggregator.problem_params[pid]
                    maxscore = params.max_score
                    minscore = params.min_score
                    if problem.group in self.aggregator.params.group_points:
                        maxscore *= float(self.aggregator.params.group_points[problem.group]) / g_score
                        minscore *= float(self.aggregator.params.group_points[problem.group]) / g_score
                    score = None
                    mscore = maxscore
                    if params.time_start_descent is not None and params.time_descent is not None:
                        mscore = self.timed_score(mscore, datetime.now(), params.time_start_descent, params.time_descent)
                    if minscore is not None and mscore < minscore:
                        mscore = minscore
                    if pid in self.scores:
                        if self.scores[pid].ok:
                            score = maxscore
                            solve_time = self.aggregator.submit_cache[self.scores[pid].ok_submit].time
                            if params.time_start_descent is not None and params.time_descent is not None:
                                score = self.timed_score(score, solve_time, params.time_start_descent, params.time_descent)
                            if minscore is not None and score < minscore:
                                score = minscore
                        else:
                            if params.obligatory:
                                all_ok = False
                    else:
                        if params.obligatory:
                            all_ok = False
                    points.append(score)
                    mpoints.append(mscore)
                problems = ' '.join([s.get_str() for s in sorted([s for s in self.scores.values() if s.ok], key=attrgetter('ok_time'))])
                score = sum([p for p in points if p is not None], 0.0)
                mscore = sum([p for p in mpoints if p is not None], 0.0)
                if not all_ok:
                    mark = 'FAIL'
                else:
                    mark = 'UNK (' + '%.2f'%(score,) + ')'

                for mrk, (lower, upper) in self.aggregator.params.points_mark:
                    if score >= lower and score < upper:
                        mark = mrk

                contestant_name = self.aggregator.table.escape(self.contestant.name)
                
                columns = ['', contestant_name]
                if self.aggregator.params.show_marks:
                    columns += [ str(mark) ]
                column = '%.2f'%(score,)
                if self.aggregator.params.show_max_score:
                    column += ' (%.2f)'%(mscore)
                columns += [column, problems]
                pi=0
                for pid in self.aggregator.sorted_problems:
                    params = self.aggregator.problem_params[pid]
                    if params.show:
                        if points[pi] is None:
                            if params.obligatory:
                                column = 'F'
                            else:
                                column = '\\-'
                            if params.show_max_score:
                                column += ' (%.2f)'%(mpoints[pi])
                            columns += [ column ]
                        else:
                            columns += [ '%.2f'%(points[pi],) ]
                    pi += 1

                self.ranking_entry.row = self.aggregator.table.generate_row(*columns) + self.aggregator.table.row_separator
                self.ranking_entry.individual = ''
                self.ranking_entry.position = self.aggregator.position(self.contestant.sort_field)
                self.ranking_entry.save()

        def aggregate(self, result):
            submit = self.aggregator.submit_cache[result.submit_id]
            if submit.problem_id not in self.scores:
                self.scores[submit.problem_id] = ACMAggregator.ACMScore.ACMProblemScore(self, self.aggregator.problem_cache[submit.problem_id])
            self.scores[submit.problem_id].aggregate(result)

    def __init__(self, supervisor, ranking):
        super(MarksAggregator, self).__init__(supervisor, ranking)

    def init(self):
        super(MarksAggregator, self).init()

        try:
            self.params.group_points = {}
            gp = yaml.load(self.params.group_points)
            for g,p in gp.iteritems():
                self.params.group_points[unicode(g)] = float(p)
        except:
            self.params.group_points = {}
        try:
            self.params.points_mark = {}
            pm = yaml.load(self.params.points_mark)
            for p,(l,u) in pm.iteritems():
                self.params.points_mark[float(p)] = (float(l), float(u))
        except:
            self.params.points_mark = {}

        for pid, params in self.problem_params.iteritems():
            if params.time_start is None:
                params.time_start = self.params.time_start
            if params.time_stop is None:
                params.time_stop = self.params.time_stop
            if params.time_start_descent is None:
                params.time_start_descent = self.params.time_start_descent
            if params.time_descent is None:
                params.time_descent = self.params.time_descent
            if params.max_score is None:
                params.max_score = self.params.max_score
            if params.min_score is None:
                params.min_score = self.params.min_score
            if params.show_max_score is None:
                params.show_max_score = self.params.show_max_score

        self.sorted_problems = [p.id for p in sorted(self.problem_cache.values(), key=attrgetter('code'))]
        columns = [(4, 'Lp.'), (32, 'Name')]
        if self.params.show_marks:
            columns += [(16, 'Mark')]
        columns += [(8, 'Score'), (16, 'Tasks')]
        self.group_score = {}
        for pid in self.sorted_problems:
            problem = self.problem_cache[pid]
            if self.problem_params[pid].show:
                columns += [(16, problem.code)]
            self.group_score[problem.group] = self.group_score.get(problem.group, 0) + self.problem_params[pid].max_score

        self.table = RestTable(*columns)
        
        self.ranking.header = self.table.row_separator + self.table.header_row + self.table.header_separator
        self.ranking.footer = ''
        self.ranking.save()
        
    def get_score(self):
        return self.MarksScore(self)


        

aggregators = {}
for item in globals().values():
    if isinstance(item, type) and issubclass(item, AggregatorBase) and (item != AggregatorBase):
        aggregators[item.__name__] = item
