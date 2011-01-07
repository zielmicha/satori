# vim:ts=4:sts=4:sw=4:expandtab

from django.db import models

from satori.core.dbev   import Events
from satori.core.models import Entity

@ExportModel
class Ranking(Entity):
    """Model. Ranking in a Contest.
    """
    parent_entity = models.OneToOneField(Entity, parent_link=True, related_name='cast_ranking')

    contest       = models.ForeignKey('Contest', related_name='rankings')
    name          = models.CharField(max_length=50)
    aggregator    = models.CharField(max_length=128)
    header        = models.TextField()
    footer        = models.TextField()
    is_public     = models.BooleanField()
    problems      = models.ManyToManyField('ProblemMapping', related_name='rankings+', through='RankingParams')

    class Meta:                                                # pylint: disable-msg=C0111
        unique_together = (('contest', 'name'),)

    class ExportMeta(object):
        fields = [('contest', 'VIEW'), ('name', 'VIEW'), ('aggregator', 'MANAGE'), ('header', 'MANAGE'), ('footer', 'MANAGE'), ('is_public', 'MANAGE')]

    @classmethod
    def inherit_rights(cls):
        inherits = super(Ranking, cls).inherit_rights()
        cls._inherit_add(inherits, 'VIEW', 'contest', 'VIEW', 'is_public', '1')
        return inherits

    def save(self, *args, **kwargs):
        from satori.core.checking.aggregators import aggregators
        if not self.aggregator in aggregators:
            raise ValueError('Aggregator '+self.aggregator+' is not allowed')
        super(Ranking,self).save(*args,**kwargs)

    @ExportMethod(unicode, [DjangoId('Ranking')], PCArg('self', 'VIEW'))
    def full_ranking(self):
        res = self.header
        res += ''.join([ entry.row for entry in self.entries.all() ])
        res += self.footer
        return res

class RankingEvents(Events):
    model = Ranking
    on_insert = on_update = ['contest', 'name']
