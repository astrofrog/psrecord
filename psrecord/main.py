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

from __future__ import (unicode_literals, division, print_function,
                        absolute_import)

import time
import argparse

children = []


def get_percent(process):
    return process.cpu_percent()

def get_memory(process):
    return process.memory_info()

def get_diskio(process):
    return process.io_counters()

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

    parser = argparse.ArgumentParser(
        description='Record CPU and memory usage for a process')

    parser.add_argument('process_id_or_command', type=str,
                        help='the process id or command')

    parser.add_argument('--log', type=str,
                        help='output the statistics to a file')

    parser.add_argument('--plot', type=str,
                        help='output the statistics to a plot')

    parser.add_argument('--duration', type=float,
                        help='how long to record for (in seconds). If not '
                             'specified, the recording is continuous until '
                             'the job exits.')

    parser.add_argument('--interval', type=float,
                        help='how long to wait between each sample (in '
                             'seconds). By default the process is sampled '
                             'as often as possible.')

    parser.add_argument('--include-children',
                        help='include sub-processes in statistics (results '
                             'in a slower maximum sampling rate).',
                        action='store_true')

    args = parser.parse_args()

    # Attach to process
    try:
        pid = int(args.process_id_or_command)
        print("Attaching to process {0}".format(pid))
        sprocess = None
    except Exception:
        import subprocess
        command = args.process_id_or_command
        print("Starting up command '{0}' and attaching to process"
              .format(command))
        sprocess = subprocess.Popen(command, shell=True)
        pid = sprocess.pid

    monitor(pid, logfile=args.log, plot=args.plot, duration=args.duration,
            interval=args.interval, include_children=args.include_children)

    if sprocess is not None:
        sprocess.kill()


def monitor(pid, logfile=None, plot=None, duration=None, interval=None,
            include_children=False):

    # We import psutil here so that the module can be imported even if psutil
    # is not present (for example if accessing the version)
    import psutil

    pr = psutil.Process(pid)

    # Record start time
    start_time = time.time()

    if logfile:
        f = open(logfile, 'w')
        f.write("# {0:12s} {1:12s} {2:12s} {3:12s} {4:12s} {5:12s}\n".format(
            'Elapsed time'.center(12),
            'CPU (%)'.center(12),
            'Real (MB)'.center(12),
            'Virtual (MB)'.center(12),
            'Disk Read (MB/s)'.center(12),
            'Disk Write (MB/s)'.center(12))
        )

    log = {}
    log['times'] = []
    log['cpu'] = []
    log['mem_real'] = []
    log['mem_virtual'] = []
    log['disk_read'] = []
    log['disk_write'] = []

    try:
        previous_time = time.time()
        current_time = time.time()
        prev_disk_read = 0
        prev_disk_write = 0
        disk_stat_started = False # there's no prev data to compare.
        # Start main event loop
        while True:
            previous_time = current_time # Save the old time for disk io calculation
            # Find current time
            current_time = time.time()

            try:
                pr_status = pr.status()
            except TypeError:  # psutil < 2.0
                pr_status = pr.status
            except psutil.NoSuchProcess:  # pragma: no cover
                break

            # Check if process status indicates we should exit
            if pr_status in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                print("Process finished ({0:.2f} seconds)"
                      .format(current_time - start_time))
                break

            # Check if we have reached the maximum time
            if duration is not None and current_time - start_time > duration:
                break

            # Get current CPU and memory
            try:
                current_cpu = get_percent(pr)
                current_mem = get_memory(pr)
                current_diskio = get_diskio(pr)
            except Exception:
                break
            current_mem_real = current_mem.rss / 1024. ** 2
            current_mem_virtual = current_mem.vms / 1024. ** 2
            current_disk_read = current_diskio.read_bytes / 1024. ** 2 # In MB
            current_disk_write = current_diskio.write_bytes / 1024. ** 2 # In MB

            # Get information for children
            if include_children:
                for child in all_children(pr):
                    try:
                        current_cpu += get_percent(child)
                        current_mem = get_memory(child)
                    except Exception:
                        continue
                    current_mem_real += current_mem.rss / 1024. ** 2
                    current_mem_virtual += current_mem.vms / 1024. ** 2

            # Calculate disk io
            disk_rd_rate = 0 # MB/s
            disk_wr_rate = 0 # MB/s
            if disk_stat_started:
                disk_rd_rate = (current_disk_read - prev_disk_read)/(current_time-previous_time)
                disk_wr_rate = (current_disk_write - prev_disk_write)/(current_time-previous_time)
                prev_disk_read = current_disk_read
                prev_disk_write = current_disk_write
            else: # If this is new disk stat, no prev data to compute rate. Leave rate to 0.
                prev_disk_read = current_disk_read
                prev_disk_write = current_disk_write
                disk_stat_started = True
    
            if logfile:
                f.write("{0:12.3f} {1:12.3f} {2:12.3f} {3:12.3f} {4:12.3f} {5:12.3f}\n".format(
                    current_time - start_time,
                    current_cpu,
                    current_mem_real,
                    current_mem_virtual,
                    disk_rd_rate,
                    disk_wr_rate))
                f.flush()

            if interval is not None:
                time.sleep(interval)

            # If plotting, record the values
            if plot:
                log['times'].append(current_time - start_time)
                log['cpu'].append(current_cpu)
                log['mem_real'].append(current_mem_real)
                log['mem_virtual'].append(current_mem_virtual)
                log['disk_read'].append(disk_rd_rate)
                log['disk_write'].append(disk_wr_rate)

    except KeyboardInterrupt:  # pragma: no cover
        pass

    if logfile:
        f.close()

    if plot:

        # Use non-interactive backend, to enable operation on headless machines
        import matplotlib.pyplot as plt
        with plt.rc_context({'backend': 'Agg'}):

            # fig = plt.figure()
            # axcpu = fig.add_subplot(1, 1, 1)
            
            fig, axcpu = plt.subplots()
            fig.subplots_adjust(right=0.75)

            axcpu.plot(log['times'], log['cpu'], '-', lw=1, color='r')

            axcpu.set_ylabel('CPU (%)', color='r')
            axcpu.set_xlabel('time (s)')
            axcpu.set_ylim(0., max(log['cpu']) * 1.2)

            axram = axcpu.twinx()

            axram.plot(log['times'], log['mem_real'], '-', lw=1, color='b')
            axram.set_ylim(0., max(log['mem_real']) * 1.2)

            axram.set_ylabel('Real Memory (MB)', color='b')

            axdisk = axcpu.twinx()
            axdisk.spines["right"].set_position(("axes", 1.2))
            prd, = axdisk.plot(log['times'], log['disk_read'], '-', lw=1, color='c', label="Disk Read")
            pwr, = axdisk.plot(log['times'], log['disk_write'], '-', lw=1, color='m', label="Disk Write")
            axdisk.set_ylim(0., max(max(log['disk_read']), max(log['disk_write'])) * 1.2)

            axdisk.set_ylabel('Disk I/O (MB/s)', color='k')
            
            lines = [prd, pwr]

            axcpu.legend(lines, [l.get_label() for l in lines])

            axcpu.grid()

            fig.savefig(plot)
