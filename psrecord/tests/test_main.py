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
            assert next(data) == ["elapsed_time", "nproc", "cpu", "mem_real", "mem_virtual"]

    def test_plot(self, tmpdir):
        pytest.importorskip("matplotlib")
        filename = tmpdir.join("test_plot.png").strpath
        monitor(self.p.pid, plot=filename, duration=3)
        assert os.path.exists(filename)

    def test_main(self):
        sys.argv = [
            "psrecord",
            "--duration=3",
            f'"{sys.executable}" -c "import time; time.sleep(10)"',
        ]
        main()

    def test_main_by_id(self):
        sys.argv = ["psrecord", "--duration=3", str(os.getpid())]
        main()

    @pytest.mark.skipif(sys.platform == "darwin", reason="Functionality not supported on MacOS")
    def test_io(self, tmpdir):
        monitor(os.getpid(), duration=3, include_io=True)


MEMORY_CODE = """
x = [0] * 20_000_000
import time
time.sleep(10)
"""


def max_logged_memory(filename):
    with open(filename) as f:
        rows = [line.split() for line in f.readlines()[1:]]
    return max(float(row[2]) for row in rows)


@pytest.mark.skipif(sys.platform == "win32", reason="Test relies on POSIX commands")
class TestLaunchedCommand:
    # When psrecord launches the command itself, the logged statistics
    # should be those of the command, not of an intermediate shell

    def setup_method(self, method):
        self.original_argv = sys.argv

    def teardown_method(self, method):
        sys.argv = self.original_argv

    def test_simple_command(self, tmpdir):
        script = tmpdir.join("memory.py").strpath
        with open(script, "w") as f:
            f.write(MEMORY_CODE)
        logfile = tmpdir.join("log.txt").strpath
        sys.argv = [
            "psrecord",
            f"{sys.executable} {script}",
            "--log",
            logfile,
            "--duration=3",
            "--interval=0.2",
        ]
        main()
        assert max_logged_memory(logfile) > 100

    def test_command_with_shell_syntax(self, tmpdir):
        script = tmpdir.join("memory.py").strpath
        with open(script, "w") as f:
            f.write(MEMORY_CODE)
        logfile = tmpdir.join("log.txt").strpath
        sys.argv = [
            "psrecord",
            f"sleep 0 && {sys.executable} {script}",
            "--log",
            logfile,
            "--duration=3",
            "--interval=0.2",
        ]
        main()
        assert max_logged_memory(logfile) > 100
