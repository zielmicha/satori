# vim:ts=4:sts=4:sw=4:expandtab

from satori.core.models import Global, Role, User

@ExportClass
class Security(object):
    """
    """
    @ExportMethod(DjangoStruct('Role'), [], PCPermit())
    @staticmethod
    def anonymous():
        return Global.get_instance().anonymous

    @ExportMethod(DjangoStruct('Role'), [], PCPermit())
    @staticmethod
    def authenticated():
        return Global.get_instance().authenticated

    @ExportMethod(DjangoStruct('Role'), [], PCPermit())
    @staticmethod
    def whoami():
        return token_container.token.role

    @ExportMethod(DjangoStruct('User'), [], PCPermit())
    @staticmethod
    def whoami_user():
        return token_container.token.user
