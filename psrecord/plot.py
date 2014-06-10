# Copyright (c) 2014, Simon Conseil
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

import argparse

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
    print("Matplotlib is not available.")


class Plot(object):
    def __init__(self):
        self.max_time = 0
        self.max_cpu = 0
        self.max_mem = 0
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax2 = self.ax.twinx()

    def plot(self, data, label=''):
        self.max_time = max(self.max_time, data['times'][-1])

        if 'cpu' in data:
            self.ax.plot(data['times'], data['cpu'], '-', lw=1,
                         label=label + ' cpu', marker='o', ms=3)
            self.max_cpu = max(self.max_cpu, max(data['cpu']) * 1.1)
        if 'mem_real' in data:
            self.ax2.plot(data['times'], data['mem_real'], '-', lw=1,
                          label=label + ' mem', marker='o', ms=3)
            self.max_mem = max(self.max_mem, max(data['mem_real']) * 1.1)

    def show(self):
        self.ax.set_xlim(0., self.max_time)
        self.ax.set_xlabel('time (s)')

        if self.max_cpu > 0:
            self.ax.set_ylabel('CPU (%)')
            self.ax.set_ylim(0., self.max_cpu)
        if self.max_mem > 0:
            self.ax2.set_ylabel('Real Memory (MB)')
            self.ax2.set_ylim(0., self.max_mem)

        self.ax.grid()
        handles, labels = self.ax.get_legend_handles_labels()
        handles2, labels2 = self.ax2.get_legend_handles_labels()
        self.ax.legend(handles + handles2, labels + labels2, loc='best')
        plt.show()

    def save(self, filename):
        self.fig.savefig(filename)


def read_file(filename):
    with open(filename, 'r') as f:
        lines = [[float(i) for i in line.split()]
                 for line in f if not line.startswith('#')]

    return zip(*lines)


def main():
    parser = argparse.ArgumentParser(
        description='Plot stats from psrecord')

    parser.add_argument('files', type=str, nargs='*',
                        help='List of files to plot')
    parser.add_argument('-m', '--mem', action='store_true',
                        help='Show memory values')
    parser.add_argument('-c', '--cpu', action='store_true',
                        help='Show cpu values')
    parser.add_argument('-o', '--output', type=str,
                        help='Save the plot to a file')
    args = parser.parse_args()

    if not args.mem and not args.cpu:
        args.mem = True
        args.cpu = True

    plot = Plot()
    for f in args.files:
        times, cpu, mem, _ = read_file(f)
        data = {'times': times}
        if args.mem:
            data['mem_real'] = mem
        if args.cpu:
            data['cpu'] = cpu
        plot.plot(data, label=f)

    plot.show()
    if args.output:
        plot.save(args.output)
