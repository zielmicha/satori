# vim:ts=4:sts=4:sw=4:expandtab
#! module models

from django.db import models
from satori.core.dbev import Events
from satori.core.models import Entity

class AttributeGroup(Entity):
    """
    """
    __module__ = "satori.core.models"
    parent_object = models.OneToOneField(Entity, parent_link=True, related_name='cast_attribute_group')


class AttributeGroupEvents(Events):
    model = AttributeGroup
    on_insert = on_update = on_delete = []
