# vim:ts=4:sts=4:sw=4:expandtab
import logging
from blist import sortedlist

class ReporterBase(object):
    def __init__(self, test_suite_result):
        super(ReporterBase, self).__init__()
        self.test_suite_result = test_suite_result

    def init(self):
        pass

    def accumulate(self, test_result):
        pass

    def status(self):
        return True

    def deinit(self):
        pass


class StatusReporter(ReporterBase):
    def __init__(self, test_suite_result):
        super(StatusReporter, self).__init__(test_suite_result)

    def init(self):
        status = self.test_suite_result.oa_get_str('status')
        if status is None:
            status = ''
        self.test_suite_result.status = status
        self.test_suite_result.report = ''
        self.test_suite_result.save()

    def accumulate(self, test_result):
        status = self.test_suite_result.oa_get_str('status')
        if status is None:
            status = ''
        self.test_suite_result.status = status
        self.test_suite_result.report = ''
        self.test_suite_result.save()

    def deinit(self):
        status = self.test_suite_result.oa_get_str('status')
        if status is None:
            status = ''
        self.test_suite_result.status = status
        self.test_suite_result.report = 'Finished checking: {0}'.format(status)
        self.test_suite_result.save()


class CountReporter(ReporterBase):
    def __init__(self, test_suite_result):
        super(CountReporter, self).__init__(test_suite_result)

    def init(self):
        self.checked = 0
        self.passed = 0
        self._status = ''
        self.reportlines = sortedlist(key=lambda row: row[0])
        self.test_suite_result.status = 'QUE'
        self.test_suite_result.report = ''
        self.test_suite_result.save()

    def accumulate(self, test_result):
        result = test_result.oa_get_str('status')
        self.checked = self.checked+1
        if result is None:
            result = 'INT'
        if result == 'OK':
            self.passed = self.passed+1
        self._status = str(self.passed) + ' / '+ str(self.checked)
        
        self.reportlines.add([test_result.test.name,result])
        self.test_suite_result.report = ' '.join(['['+str(r[0])+':'+str(r[1])+']' for r in self.reportlines])
        self.test_suite_result.save()
        
    def status(self):
        return True

    def deinit(self):
        self.test_suite_result.status = self._status
        self.test_suite_result.oa_set_str('status', self._status)
        self.test_suite_result.oa_set_str('checked', self.checked)
        self.test_suite_result.oa_set_str('passed', self.passed)
        self.test_suite_result.save()


reporters = {}
for item in globals().values():
    if isinstance(item, type) and issubclass(item, ReporterBase) and (item != ReporterBase):
        reporters[item.__name__] = item
