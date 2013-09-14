
import re

from buildbot.process.buildstep import LogLineObserver
from buildbot.steps.shell import ShellCommand
from buildbot.status.results import SUCCESS, FAILURE, WARNINGS

class LoggedUnitTest(ShellCommand):
    def __init__(self, *args, **kwargs):
        ShellCommand.__init__(self, *args, **kwargs)
        self.testResults = []
        testObserver =  UnitTestsObserver()
        self.addLogObserver('stdio', testObserver)

    def createSummary(self, log):
        self.setProperty("failed_tests", len(self.testResults))
        self.addHTMLLog(
            'Tests: %d failures and errors' % (len(self.testResults),),
            ''.join('<b>%s</b><pre>%s</pre>' % t for t in self.testResults)
        )

    def evaluateCommand(self, cmd):
        if self.getProperty("failed_tests"):
            return FAILURE
        return SUCCESS


class UnitTestsObserver(LogLineObserver):
    def __init__(self):
        LogLineObserver.__init__(self)
        self.in_fail_output = False
        self.re_fail = [
            (re.compile('^(FAIL:) (.*)$'), 1),
            (re.compile('^(ERROR:) (.*)$'), 1)
        ]
        self.re_startendtest = re.compile('^------------------------------|^=========================')

    def errLineReceived(self, line):
        self.outLineReceived(line)

    def outLineReceived(self, line):
        if self.in_fail_output:
            result = self.re_startendtest.search(line)
            if result:
                if len(self.fail_output) > 0:
                    self.fail_output.append(line)
                    self.step.testResults.append((self.test_name, '\n'.join(self.fail_output)))
                    self.in_fail_output = False
            self.fail_output.append(line)
            return
        for r in self.re_fail:
            result = r[0].search(line)
            if result:
                self.test_name = result.groups()[r[1]].strip()
                self.in_fail_output = True
                self.fail_output = []
