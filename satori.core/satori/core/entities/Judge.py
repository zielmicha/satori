# vim:ts=4:sts=4:sw=4:expandtab


"""
Judge helper procedures.
"""

from types import NoneType

from satori.core.checking.check_queue_client import CheckQueueClient
from satori.core.dbev               import Events

from satori.core.models import Role

SubmitToCheck = Struct('SubmitToCheck', (
    ('test_result', DjangoId(TestResult), True),
    ('test_data', TypedMap(unicode, AnonymousAttribute), False),
    ('submit_data', TypedMap(unicode, AnonymousAttribute), False),
))


@ExportClass
class Judge(object):

    @ExportMethod(SubmitToCheck, [], PCAnd(PCTokenIsMachine(), PCGlobal('JUDGE')))
    @staticmethod
    def get_next():
        m = token_container.token.machine

        next = CheckQueueClient.get_instance().get_next(m)

        if next.test_result_id is None:
            return None

        ret = SubmitToCheck()
        ret.test_result = TestResult.objects.get(id=next.test_result_id)
        ret.test_data = ret.test_result.test.data_get_map()
        ret.submit_data = ret.test_result.submit.data_get_map()

        return ret

    @ExportMethod(NoneType, [DjangoId('TestResult'), TypedMap(unicode, AnonymousAttribute)], PCGlobal('JUDGE'))
    @staticmethod
    def set_result(test_result, result):
        test_result.oa_set_map(result)
        test_result.pending = False
        test_result.save()

