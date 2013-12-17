import os
import sys
import subprocess

from ..main import main, monitor


class TestMonitor(object):

    def setup_method(self, method):
        self.p = subprocess.Popen('sleep 10', shell=True)

    def teardown_method(self, method):
        self.p.kill()

    def test_simple(self):
        monitor(self.p.pid, duration=3)

    def test_simple_with_interval(self):
        monitor(self.p.pid, duration=3, interval=0.1)

    def test_logfile(self, tmpdir):
        filename = tmpdir.join('test_logfile').strpath
        monitor(self.p.pid, logfile=filename, duration=3)
        assert os.path.exists(filename)
        assert len(open(filename, 'r').readlines()) > 0

    def test_plot(self, tmpdir):
        filename = tmpdir.join('test_plot.png').strpath
        monitor(self.p.pid, plot=filename, duration=3)
        assert os.path.exists(filename)

    def test_main(self):
        orig = sys.argv[:]
        sys.argv = 'psrecord {0} --duration=3'.split()
        main()
