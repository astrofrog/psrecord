|Build Status| |Coverage Status|

About
=====

``psrecord`` is a small utility that uses the
`psutil <https://github.com/giampaolo/psutil/>`__ library to record the CPU
and memory activity of a process. The package is still under development
and is therefore experimental.

The code is released under a Simplified BSD License, which is given in
the ``LICENSE`` file.

Requirements
============

-  Python 2.7 or 3.3 and higher
-  `psutil <https://code.google.com/p/psutil/>`__ 1.0 or later
-  `matplotlib <http://www.matplotlib.org>`__ (optional, used for
   plotting)

Installation
============

To install, simply do::

    pip install psrecord

Usage
=====

Basics
------

To record the CPU and memory activity of an existing process to a file (use sudo for a root process):

::

    psrecord 1330 --log activity.txt

where ``1330`` is an example of a process ID which you can find with
``ps`` or ``top``. You can also use ``psrecord`` to start up a process
by specifying the command in quotes:

::

    psrecord "hyperion model.rtin model.rtout" --log activity.txt

Plotting
--------

To make a plot of the activity:

::

    psrecord 1330 --plot plot.png

This will produce a plot such as:

.. image:: https://github.com/astrofrog/psrecord/raw/master/screenshot.png

You can combine these options to write the activity to a file and make a
plot at the same time:

::

    psrecord 1330 --log activity.txt --plot plot.png

Duration and intervals
----------------------

By default, the monitoring will continue until the process is stopped.
You can also specify a maximum duration in seconds:

::

    psrecord 1330 --log activity.txt --duration 10

Finally, the process is polled as often as possible by default, but it
is possible to set the time between samples in seconds:

::

    psrecord 1330 --log activity.txt --interval 2

Subprocesses
------------

To include sub-processes in the CPU and memory stats, use:

::

    psrecord 1330 --log activity.txt --include-children

Running tests
=============

To run tests, you will need `pytest <https://docs.pytest.org/en/latest/>`_. You can install it with::

    pip install pytest
    
You can then run the tests with::

    pytest psrecord

Reporting issues
================

Please report any issues in the `issue
tracker <https://github.com/astrofrog/psrecord/issues>`__.

.. |Build Status| image:: https://travis-ci.org/astrofrog/psrecord.svg?branch=master
   :target: https://travis-ci.org/astrofrog/psrecord
.. |Coverage Status| image:: https://codecov.io/gh/astrofrog/psrecord/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/astrofrog/psrecord
