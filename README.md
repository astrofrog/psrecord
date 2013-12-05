About
=====

``psrecord`` is a small utility that uses the
[psutil](https://code.google.com/p/psutil/) library to record the CPU and
memory activity of a process. The package is still under development and is
therefore experimental.

Requirements
============

* [psutil](https://code.google.com/p/psutil/)
* [matplotlib](http://www.matplotlib.org) (optional, used for plotting)

Installation
============

To install:

    git clone https://github.com/astrofrog/psrecord
    cd psrecord
    python setup.py install

Usage
=====

To record the CPU and memory activity of a process to a file:

    psrecord process_id --log activity.txt

where ``process_id`` is a process ID such as ``1293`` or ``10022``.

To make a plot of the activity:

    psrecord process_id --plot plot.png

You can combine these options to write the activity to a file and make a plot
at the same time:

    psrecord process_id --log activity.txt --plot plot.png

By default, the monitoring will continue until the process is stopped. You can
also specify a maximum duration in seconds:

    psrecord process_id --log activity.txt --duration 10

Finally, the process is polled as often as possible by default, but it is
possible to set the time between samples in seconds:

    psrecord process_id --log activity.txt --interval 2

Reporting issues
================

Please report any issues in the
[issue tracker](https://github.com/astrofrog/psrecord/issues).

