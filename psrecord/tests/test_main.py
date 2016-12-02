import os
import sys
import subprocess

import psutil
from ..main import main, monitor, all_children

TEST_CODE = """
import subprocess
p = subprocess.Popen('sleep 5'.split())
p.wait()
"""


def test_all_children(tmpdir):

    filename = tmpdir.join('test.py').strpath

    with open(filename, 'w') as f:
        f.write(TEST_CODE)

    p = subprocess.Popen('{0} {1}'.format(sys.executable, filename).split())

    import time
    time.sleep(1)

    pr = psutil.Process(p.pid)
    children = all_children(pr)
    assert len(children) > 0
    p.kill()


class TestMonitor(object):

    def setup_method(self, method):
        self.p = subprocess.Popen('sleep 10', shell=True)

    def teardown_method(self, method):
        self.p.kill()

    def test_simple(self):
        monitor(self.p.pid, duration=3)

    def test_simple_with_interval(self):
        monitor(self.p.pid, duration=3, interval=0.1)

    def test_with_children(self, tmpdir):
        # Test with current process since it has a subprocess (self.p)
        monitor(os.getpid(), duration=3, include_children=True)

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
        sys.argv = ['psrecord', '--duration=3', "'sleep 10'"]
        main()

    def test_main_by_id(self):
        sys.argv = ['psrecord', '--duration=3', str(os.getpid())]
        main()
