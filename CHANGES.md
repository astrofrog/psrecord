1.2 (2020-05-28)
----------------

- Fixed compatibility with latest versions of psutil and fixed issue with
  determining CPU usage from child processes. [#56]

- Fixed plotting to work on machines where Agg is not the default
  Matplotlib backend. [#44]

1.1 (2018-06-16)
----------------

- Fixed installation via pip if psutil was not installed. [#37]

1.0 (2016-12-05)
----------------

- Fix compatibility with recent versions of psutil. [#18, #19]

- psutil is now properly defined as a dependency in install_requires. [#16]

0.2 (2014-10-22)
----------------

- Recognize zombie processes. [#7]

- Improve general reliability.

- Allow interval to be a floating-point value.

- Fix compatibility with psutil >= 2.0. [#10]

- Ensure that log file gets closed and plot gets drawn if process is
  interrupted. [#13]

0.1 (2013-12-17)
----------------

- Initial release
