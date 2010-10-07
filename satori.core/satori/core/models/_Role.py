# vim:ts=4:sts=4:sw=4:expandtab

from django.db import models
from satori.dbev import Events
from satori.core.models._Entity import Entity

class Role(Entity):
    """Model. Base for authorization "levels".
    """
    __module__ = "satori.core.models"
    parent_object = models.OneToOneField(Entity, parent_link=True, related_name='cast_role')

    name        = models.CharField(max_length=50)
    absorbing   = models.BooleanField(default=False)
    children    = models.ManyToManyField("self", related_name='parents', through='RoleMapping', symmetrical=False)

class RoleEvents(Events):
    model = Role
    on_insert = on_update = ['name']
    on_delete = []

