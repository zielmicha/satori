# vim:ts=4:sts=4:sw=4:expandtab

from django.db import models

from satori.core.dbev   import Events
from satori.core.models import Entity

class RankingEntry(Entity):
    """Model. Ranking in a Contest.
    """
    parent_entity = models.OneToOneField(Entity, parent_link=True, related_name='cast_rankingentry')

    ranking       = models.ForeignKey('Ranking', related_name='entries', on_delete=models.CASCADE)
    contestant    = models.ForeignKey('Contestant', related_name='ranking_entries+', on_delete=models.CASCADE)
    row           = models.TextField()
    individual    = models.TextField()
    position      = models.CharField(max_length=64)

    class Meta:                                                # pylint: disable-msg=C0111
        unique_together = (('contestant', 'ranking'),)
        ordering        = ('position',)

class RankingEntryEvents(Events):
    model = RankingEntry
    on_insert = on_update = []
