import csv
import os
import subprocess
import sys

import psutil
import pytest

from ..main import all_children, main, monitor

TEST_CODE = """
import subprocess
p = subprocess.Popen('sleep 5'.split())
p.wait()
"""


def test_all_children(tmpdir):
    filename = tmpdir.join("test.py").strpath

    with open(filename, "w") as f:
        f.write(TEST_CODE)

    p = subprocess.Popen(f"{sys.executable} {filename}".split())

    import time

    time.sleep(1)

    pr = psutil.Process(p.pid)
    children = all_children(pr)
    assert len(children) > 0
    p.kill()


class TestMonitor:
    def setup_method(self, method):
        self.p = subprocess.Popen("sleep 10", shell=True)

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
        filename = tmpdir.join("test_logfile").strpath
        monitor(self.p.pid, logfile=filename, duration=3)
        assert os.path.exists(filename)
        assert len(open(filename).readlines()) > 0

    def test_logfile_csv(self, tmpdir):
        filename = tmpdir.join("test_logfile.csv").strpath
        monitor(self.p.pid, logfile=filename, duration=3, log_format="csv")
        assert os.path.exists(filename)
        assert len(open(filename).readlines()) > 0
        with open(filename) as csvfile:
            data = csv.reader(csvfile)
            assert next(data) == ["elapsed_time", "cpu", "mem_real", "mem_virtual"]

    def test_plot(self, tmpdir):
        pytest.importorskip("matplotlib")
        filename = tmpdir.join("test_plot.png").strpath
        monitor(self.p.pid, plot=filename, duration=3)
        assert os.path.exists(filename)

    def test_main(self):
        sys.argv = ["psrecord", "--duration=3", "'sleep 10'"]
        main()

    def test_main_by_id(self):
        sys.argv = ["psrecord", "--duration=3", str(os.getpid())]
        main()

    @pytest.mark.skipif(sys.platform == "darwin", reason="Functionality not supported on MacOS")
    def test_io(self, tmpdir):
        monitor(os.getpid(), duration=3, include_io=True)
