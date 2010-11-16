# vim:ts=4:sts=4:sw=4:expandtab

class PCPermit(object):
    def __call__(__pc__self, **kwargs):
        return True

    def  __str__(__pc__self):
        return 'none'


class PCArg(object):
    def __init__(__pc__self, name, perm):
        super(PCArg, __pc__self).__init__()
        __pc__self.name = name
        __pc__self.perm = perm

    def __call__(__pc__self, **kwargs):
        return Privilege.demand(kwargs[__pc__self.name], __pc__self.perm)

    def __str__(__pc__self):
        return '{0} on {1}'.format(__pc__self.perm, __pc__self.name)


class PCGlobal(object):
    def __init__(__pc__self, perm):
        super(PCGlobal, __pc__self).__init__()
        __pc__self.perm = perm

    def __call__(__pc__self, **kwargs):
        return Privilege.global_demand(__pc__self.perm)

    def __str__(__pc__self):
        return 'global {0}'.format(__pc__self.perm)


class PCAnd(object):
    def __init__(__pc__self, *subs):
        super(PCAnd, __pc__self).__init__()
        __pc__self.subs = subs

    def __call__(__pc__self, **kwargs):
        return all(x(**kwargs) for x in __pc__self.subs)

    def __str__(__pc__self):
        return '(' + ') and ('.join(str(p) for p in __pc__self.subs) + ')'

class PCOr(object):
    def __init__(__pc__self, *subs):
        super(PCOr, __pc__self).__init__()
        __pc__self.subs = subs

    def __call__(__pc__self, **kwargs):
        return any(x(**kwargs) for x in __pc__self.subs)
    
    def __str__(__pc__self):
        return '(' + ') or ('.join(str(p) for p in __pc__self.subs) + ')'


class PCEach(object):
    def __init__(__pc__self, name, sub):
        super(PCEach, __pc__self).__init__()
        __pc__self.name = name
        __pc__self.sub = sub

    def __call__(__pc__self, **kwargs):
        return all(__pc__self.sub(item=x) for x in kwargs[__pc__self.name])

    def __str__(__pc__self):
        return 'for every item in {0}: {1}'.format(__pc__self.name, str(__pc__self.sub))


class PCEachKey(object):
    def __init__(__pc__self, name, sub):
        super(PCEachKey, __pc__self).__init__()
        __pc__self.name = name
        __pc__self.sub = sub

    def __call__(__pc__self, **kwargs):
        return all(__pc__self.sub(item=x) for x in kwargs[__pc__self.name].keys())

    def __str__(__pc__self):
        return 'for every item in {0}.keys(): {1}'.format(__pc__self.name, str(__pc__self.sub))


class PCEachValue(object):
    def __init__(__pc__self, name, sub):
        super(PCEachValue, __pc__self).__init__()
        __pc__self.name = name
        __pc__self.sub = sub

    def __call__(__pc__self, **kwargs):
        return all(__pc__self.sub(item=x) for x in kwargs[__pc__self.name].values())

    def __str__(__pc__self):
        return 'for every item in {0}.values(): {1}'.format(__pc__self.name, str(__pc__self.sub))


class PCTokenUser(object):
    def __init__(__pc__self, name):
        super(PCTokenUser, __pc__self).__init__()
        __pc__self.name = name

    def __call__(__pc__self, **kwargs):
        return token_container.token.user_id == kwargs[__pc__self.name].id

    def __str__(__pc__self):
        return '{0} equals to calling user'.format(__pc__self.name)


class PCRawBlob(object):
    def __init__(__pc__self, name):
        super(PCRawBlob, __pc__self).__init__()
        __pc__self.name = name

    def __call__(__pc__self, **kwargs):
        if kwargs[__pc__self.name].is_blob:
            return Privilege.global_demand('RAW_BLOB')
        else:
            return True

    def __str__(__pc__self):
        return 'global RAW_BLOB if {0}.is_blob = True'.format(__pc__self.name)


def init():
    global Privilege
    from satori.core.models import Privilege
