from __future__ import unicode_literals, division, print_function, absolute_import

import sys
import psutil
import time
import argparse


def all_children(pr):
    processes = []
    for child in pr.get_children():
        processes.append(child)
        processes += all_children(child)
    return processes


def main():

    parser = argparse.ArgumentParser(description='Record CPU and memory usage for a process')

    parser.add_argument('process_id_or_command', type=str, help='the process id or command')

    parser.add_argument('--log', type=str,
                        help='output the statistics to a file')

    parser.add_argument('--plot', type=str,
                        help='output the statistics to a plot')

    parser.add_argument('--duration', type=float,
                        help='how long to record for (in seconds). If not '
                             'specified, the recording is continuous until '
                             'the job exits.')

    parser.add_argument('--interval', type=int,
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
    except:
        import subprocess
        command = args.process_id_or_command
        print("Starting up command '{0}' and attaching to process".format(command))
        sprocess = subprocess.Popen(command, shell=True)
        pid = sprocess.pid

    pr = psutil.Process(pid)

    # Record start time
    start_time = time.time()

    if args.log:
        f = open(args.log, 'w')
        f.write("# {0:12s} {1:12s} {2:12s} {3:12s}\n".format('Elapsed time'.center(12),
                                                             'CPU (%)'.center(12),
                                                             'Real (MB)'.center(12),
                                                             'Virtual (MB)'.center(12)))

    log = {}
    log['times'] = []
    log['cpu'] = []
    log['mem_real'] = []
    log['mem_virtual'] = []

    # Start main event loop
    while True:

        # Find current time
        current_time = time.time()

        # Check if we have reached the maximum time
        if args.duration is not None and current_time - start_time > args.duration:
            break

        # Get current CPU and memory
        try:
            current_cpu = pr.get_cpu_percent()
            current_mem = pr.get_memory_info()
        except:
            break
        current_mem_real = current_mem.rss / 1024. ** 2
        current_mem_virtual = current_mem.vms / 1024. ** 2

        # Get information for children
        if args.include_children:
            for child in all_children(pr):
                try:
                    current_cpu += child.get_cpu_percent()
                    current_mem = child.get_memory_info()
                except:
                    continue
                current_mem_real += current_mem.rss / 1024. ** 2
                current_mem_virtual += current_mem.vms / 1024. ** 2

        if args.log:
            f.write("{0:12.3f} {1:12.3f} {2:12.3f} {3:12.3f}\n".format(current_time - start_time,
                                                                       current_cpu,
                                                                       current_mem_real,
                                                                       current_mem_virtual))
            f.flush()

        if args.interval is not None:
            time.sleep(args.interval)

        # If plotting, record the values
        if args.plot:
            log['times'].append(current_time - start_time)
            log['cpu'].append(current_cpu)
            log['mem_real'].append(current_mem_real)
            log['mem_virtual'].append(current_mem_virtual)

    if args.log:
        f.close()

    if len(log['times']) == 0:
        print("No samples were taken before job terminated")
        sys.exit(0)

    if args.plot:

        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)

        ax.plot(log['times'],log['cpu'], '-', lw=1, color='r')

        ax.set_ylabel('CPU (%)', color='r')
        ax.set_xlabel('time (s)')
        ax.set_ylim(0., max(log['cpu']) * 1.2)

        ax2 = ax.twinx()

        ax2.plot(log['times'],log['mem_real'], '-', lw=1, color='b')
        ax2.set_ylim(0., max(log['mem_real']) * 1.2)

        ax2.set_ylabel('Real Memory (MB)', color='b')

        ax.grid()

        fig.savefig(args.plot)

    if sprocess is not None:
        sprocess.kill()
