# Copyright (c) 2013, Thomas P. Robitaille
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import argparse
import sys
import time

children = []


def get_percent(process):
    return process.cpu_percent()


def get_memory(process):
    return process.memory_info()


def all_children(pr):
    global children

    try:
        children_of_pr = pr.children(recursive=True)
    except Exception:  # pragma: no cover
        return children

    for child in children_of_pr:
        if child not in children:
            children.append(child)

    return children


def main():
    parser = argparse.ArgumentParser(description="Record CPU and memory usage for a process")

    parser.add_argument("process_id_or_command", type=str, help="the process id or command.")

    parser.add_argument(
        "--log",
        type=str,
        help="output the statistics to a file. If neither "
        "--log nor --plot are specified, print to print "
        "to standard output.",
    )

    parser.add_argument(
        "--log-format",
        type=str,
        default="plain",
        help='the format of the log file, can be one of "plain" or "csv"',
    )

    parser.add_argument("--plot", type=str, help="output the statistics to a plot.")

    parser.add_argument(
        "--duration",
        type=float,
        help="how long to record for (in seconds). If not "
        "specified, the recording is continuous until "
        "the job exits.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        help="how long to wait between each sample (in "
        "seconds). By default the process is sampled "
        "as often as possible.",
    )

    parser.add_argument(
        "--include-children",
        help="include sub-processes in statistics (results " "in a slower maximum sampling rate).",
        action="store_true",
    )

    parser.add_argument("--include-io", help="include include_io I/O stats", action="store_true")

    args = parser.parse_args()

    # Attach to process
    try:
        pid = int(args.process_id_or_command)
        print(f"Attaching to process {pid}")
        sprocess = None
    except Exception:
        import subprocess

        command = args.process_id_or_command
        print(f"Starting up command '{command}' and attaching to process")
        sprocess = subprocess.Popen(command, shell=True)
        pid = sprocess.pid

    monitor(
        pid,
        logfile=args.log,
        plot=args.plot,
        duration=args.duration,
        interval=args.interval,
        include_children=args.include_children,
        include_io=args.include_io,
        log_format=args.log_format,
    )

    if sprocess is not None:
        sprocess.kill()


def monitor(
    pid,
    logfile=None,
    plot=None,
    duration=None,
    interval=None,
    include_children=False,
    include_io=False,
    log_format="plain",
):
    # We import psutil here so that the module can be imported even if psutil
    # is not present (for example if accessing the version)
    import psutil

    pr = psutil.Process(pid)

    # Record start time
    start_time = time.time()

    f = None
    if logfile is None and plot is None:
        f = sys.stdout
        logfile = "<stdout>"
    elif logfile is not None:
        f = open(logfile, "w")

    if logfile:
        if log_format == "plain":
            f.write(
                "# {:12s} {:12s} {:12s} {:12s}".format(
                    "Elapsed time".center(12),
                    "CPU (%)".center(12),
                    "Real (MB)".center(12),
                    "Virtual (MB)".center(12),
                ),
            )
            if include_io:
                f.write(
                    " {:12s} {:12s} {:12s} {:12s}".format(
                        "Read count".center(12),
                        "Write count".center(12),
                        "Read bytes".center(12),
                        "Write bytes".center(12),
                    )
                )
        elif log_format == "csv":
            f.write("elapsed_time,cpu,mem_real,mem_virtual")
            if include_io:
                f.write(",read_count,write_count,read_bytes,write_bytes")
        else:
            raise ValueError(
                f"Unknown log format: '{log_format}', should be either 'plain' or 'csv'"
            )
        f.write("\n")

    log = {}
    log["times"] = []
    log["cpu"] = []
    log["mem_real"] = []
    log["mem_virtual"] = []

    if include_io:
        log["read_count"] = []
        log["write_count"] = []
        log["read_bytes"] = []
        log["write_bytes"] = []

    try:
        # Start main event loop
        while True:
            # Find current time
            current_time = time.time()
            elapsed_time = current_time - start_time

            try:
                pr_status = pr.status()
            except TypeError:  # psutil < 2.0
                pr_status = pr.status
            except psutil.NoSuchProcess:  # pragma: no cover
                break

            # Check if process status indicates we should exit
            if pr_status in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                print(f"Process finished ({elapsed_time:.2f} seconds)")
                break

            # Check if we have reached the maximum time
            if duration is not None and elapsed_time > duration:
                break

            # Get current CPU and memory
            try:
                current_cpu = get_percent(pr)
                current_mem = get_memory(pr)
            except Exception:
                break
            current_mem_real = current_mem.rss / 1024.0**2
            current_mem_virtual = current_mem.vms / 1024.0**2

            if include_io:
                counters = pr.io_counters()
                read_count = counters.read_count
                write_count = counters.write_count
                read_bytes = counters.read_bytes
                write_bytes = counters.write_bytes

            # Get information for children
            if include_children:
                for child in all_children(pr):
                    try:
                        current_cpu += get_percent(child)
                        current_mem = get_memory(child)
                        current_mem_real += current_mem.rss / 1024.0**2
                        current_mem_virtual += current_mem.vms / 1024.0**2
                        if include_io:
                            counters = child.io_counters()
                            read_count += counters.read_count
                            write_count += counters.write_count
                            read_bytes += counters.read_bytes
                            write_bytes += counters.write_bytes
                    except Exception:
                        continue

            if logfile:
                if log_format == "plain":
                    f.write(
                        f"{elapsed_time:12.3f} {current_cpu:12.3f}"
                        f" {current_mem_real:12.3f} {current_mem_virtual:12.3f}"
                    )
                    if include_io:
                        f.write(
                            f" {read_count:12d} {write_count:12d}"
                            f" {read_bytes:12d} {write_bytes:12d}"
                        )
                elif log_format == "csv":
                    f.write(
                        f"{elapsed_time},{current_cpu},{current_mem_real},{current_mem_virtual}"
                    )
                    if include_io:
                        f.write(f"{read_count},{write_count},{read_bytes},{write_bytes}")
                f.write("\n")
                f.flush()

            if interval is not None:
                time.sleep(interval)

            # If plotting, record the values
            if plot:
                log["times"].append(elapsed_time)
                log["cpu"].append(current_cpu)
                log["mem_real"].append(current_mem_real)
                log["mem_virtual"].append(current_mem_virtual)
                if include_io:
                    log["read_count"].append(read_count)
                    log["write_count"].append(write_count)
                    log["read_bytes"].append(read_bytes)
                    log["write_bytes"].append(write_bytes)

    except KeyboardInterrupt:  # pragma: no cover
        pass

    # close the logfile, if it's not stdout
    if logfile and logfile != "<stdout>":
        f.close()

    if plot:
        # Use non-interactive backend, to enable operation on headless machines
        # We import matplotlib here so that the module can be imported even if
        # matplotlib is not present and the plotting option is unset
        import matplotlib.pyplot as plt

        with plt.rc_context({"backend": "Agg"}):
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)

            ax.plot(log["times"], log["cpu"], "-", lw=1, color="r")

            ax.set_ylabel("CPU (%)", color="r")
            ax.set_xlabel("time (s)")
            ax.set_ylim(0.0, max(log["cpu"]) * 1.2)

            ax2 = ax.twinx()

            ax2.plot(log["times"], log["mem_real"], "-", lw=1, color="b")
            ax2.set_ylim(0.0, max(log["mem_real"]) * 1.2)

            ax2.set_ylabel("Real Memory (MB)", color="b")

            ax.grid()

            fig.savefig(plot)
