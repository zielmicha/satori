# vim:ts=4:sts=4:sw=4:expandtab

from django.db import models
from satori.dbev import Events
from satori.core.models._Object import Object

class Submit(Object):
    """Model. Single problem solution (within or outside of a Contest).
    """
    __module__ = "satori.core.models"
    parent_object = models.OneToOneField(Object, parent_link=True, related_name='cast_submit')

    contestant  = models.ForeignKey('Contestant')
    problem     = models.ForeignKey('ProblemMapping')
    time        = models.DateTimeField(auto_now_add=True)
    
    def inherit_right(self, right):
        right = str(right)
        ret = super(Submit, self).inherit_right(right)
        if right == 'VIEW':
            ret.append((self.contestant.contest,'OBSERVE'))
        if right == 'OVERRIDE':
            ret.append((self.contestant.contest,'MANAGE'))
        return ret

class SubmitEvents(Events):
    model = Submit
    on_insert = on_update = ['owner', 'problem']
    on_delete = []


