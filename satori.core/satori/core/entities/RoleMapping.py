# vim:ts=4:sts=4:sw=4:expandtab

from django.db import models

from satori.core.dbev   import Events
from satori.core.models import Entity

class RoleMapping(Entity):
    """Model. Intermediary for many-to-many relationship between Roles.
    """
    parent_entity = models.OneToOneField(Entity, parent_link=True, related_name='cast_rolemapping')

    parent     = models.ForeignKey('Role', related_name='childmap', on_delete=models.CASCADE)
    child      = models.ForeignKey('Role', related_name='parentmap', on_delete=models.CASCADE)

    class Meta:                                                # pylint: disable-msg=C0111
        unique_together = (('parent', 'child'),)

class RoleMappingEvents(Events):
    model = RoleMapping
    on_insert = on_update = ['parent', 'child']
    on_delete = []
