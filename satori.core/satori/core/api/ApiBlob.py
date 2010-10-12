# vim:ts=4:sts=4:sw=4:expandtab

from types import NoneType
from satori.ars.wrapper import StaticWrapper
from satori.core.models import Global, OpenAttribute
from satori.core.sec import Token
from satori.objects import Argument, ReturnValue

blob = StaticWrapper('Blob')

@blob.method
@Argument('token', type=Token)
@ReturnValue(type=NoneType)
def create(token):
    raise Exception('Not implemented.')

@blob.method
@Argument('token', type=Token)
@Argument('hash', type=unicode)
@ReturnValue(type=NoneType)
def open(token, hash):
    raise Exception('Not implemented.')

@blob.method
@Argument('token', type=Token)
@Argument('hash', type=unicode)
@ReturnValue(type=bool)
def exists(token, hash):
    return OpenAttribute.exists_blob(hash)

@blob.create.can
@blob.open.can
@blob.exists.can
def create_can(token, *args, **kwargs):
    return Global.get_instance().demand_right(token, 'RAW_BLOB')

blob._fill_module(__name__)
