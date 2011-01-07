# vim:ts=4:sts=4:sw=4:expandtab

import logging

from django.db import models, DatabaseError

from satori.core.dbev   import Events
from satori.core.models import Entity

@ExportModel
class Role(Entity):
    """Model. Base for authorization "levels".
    """
    parent_entity = models.OneToOneField(Entity, parent_link=True, related_name='cast_role')

    name          = models.CharField(max_length=50)
    children      = models.ManyToManyField('self', related_name='parents', through='RoleMapping', symmetrical=False)

    class ExportMeta(object):
        fields = [('name', 'VIEW')]

    @classmethod
    def inherit_rights(cls):
        inherits = super(Role, cls).inherit_rights()
        cls._inherit_add(inherits, 'EDIT', 'id', 'MANAGE')
        cls._inherit_add(inherits, 'VIEW', 'id', 'EDIT')
        return inherits

    def __str__(self): #TODO
        return self.name

    @ExportMethod(DjangoStruct('Role'), [DjangoStruct('Role'), DjangoIdList('Role')], PCGlobal('MANAGE_PRIVILEGES'), [CannotSetField])
    @staticmethod
    def create(fields, children=[]):
        role = Role()
        role.forbid_fields(fields, ['id'])
        role.update_fields(fields, ['name'])
        role.save()
        for child in children:
            role.add_member(child)
        Privilege.grant(token_container.token.role, role, 'MANAGE')
        return role

    @ExportMethod(DjangoStruct('Role'), [DjangoId('Role'), DjangoStruct('Role')], PCArg('self', 'EDIT'), [CannotSetField])
    def modify(self, fields):
        if self.model == 'core.role':
            self.forbid_fields(fields, ['id'])
            self.update_fields(fields, ['name'])
        else:
            self.forbid_fields(fields, ['id', 'name'])
        self.save()
        return self

    #@ExportMethod(NoneType, [DjangoId('Role')], PCArg('self', 'MANAGE'), [CannotDeleteObject])
    def delete(self):
        logging.error('role deleted') #TODO: Waiting for non-cascading deletes in django
        self.privileges.all().delete()
        self.children.all().delete()
        try:
            super(Role, self).delete()
        except DatabaseError:
            raise CannotDeleteObject()

    @ExportMethod(DjangoStructList('Role'), [DjangoId('Role')], PCArg('self', 'VIEW'))
    def get_members(self):
        return self.children.all()

    @ExportMethod(NoneType, [DjangoId('Role'), DjangoId('Role')], PCArg('self', 'MANAGE'))
    def add_member(self, member):
        RoleMapping.objects.get_or_create(parent=self, child=member)[0].save()
        for c in Contestant.objects.filter(id=self.id):
            c.update_usernames()

    @ExportMethod(NoneType, [DjangoId('Role'), DjangoId('Role')], PCArg('self', 'MANAGE'))
    def delete_member(self, member):
        try:
            RoleMapping.objects.get(parent=self, child=member).delete()
        except RoleMapping.DoesNotExist:
            pass
        else:
            for c in Contestant.objects.filter(id=self.id):
                c.update_usernames()


class RoleEvents(Events):
    model = Role
    on_insert = on_update = ['name']
    on_delete = []
