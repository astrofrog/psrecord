## v1.4 - 2024-04-26

### What's Changed

* FIx CSV output (missing comma) and include number of processes in CSV output by @astrofrog in https://github.com/astrofrog/psrecord/pull/76

**Full Changelog**: https://github.com/astrofrog/psrecord/compare/v1.3...v1.4

## v1.3 - 2024-04-26

### What's Changed

* Updated package infrastructure by @astrofrog in https://github.com/astrofrog/psrecord/pull/73
* setup.py: Add matplotlib by @JohnAZoidberg in https://github.com/astrofrog/psrecord/pull/53
* If neither --log nor --plot is passed, log to stdout. Closes #50 by @CristianCantoro in https://github.com/astrofrog/psrecord/pull/68
* Add Monitor as exposed function by @Vincent-CIRCL in https://github.com/astrofrog/psrecord/pull/54
* Added ability to include I/O stats in output by @astrofrog in https://github.com/astrofrog/psrecord/pull/74
* Add support for csv and modernise code by @astrofrog in https://github.com/astrofrog/psrecord/pull/75

### New Contributors

* @JohnAZoidberg made their first contribution in https://github.com/astrofrog/psrecord/pull/53
* @CristianCantoro made their first contribution in https://github.com/astrofrog/psrecord/pull/68
* @Vincent-CIRCL made their first contribution in https://github.com/astrofrog/psrecord/pull/54

**Full Changelog**: https://github.com/astrofrog/psrecord/compare/v1.2...v1.3

## 1.2 (2020-05-28)

- Fixed compatibility with latest versions of psutil and fixed issue with
  determining CPU usage from child processes. [#56]
  
- Fixed plotting to work on machines where Agg is not the default
  Matplotlib backend. [#44]
  

## 1.1 (2018-06-16)

- Fixed installation via pip if psutil was not installed. [#37]

## 1.0 (2016-12-05)

- Fix compatibility with recent versions of psutil. [#18, #19]
  
- psutil is now properly defined as a dependency in install_requires. [#16]
  

## 0.2 (2014-10-22)

- Recognize zombie processes. [#7]
  
- Improve general reliability.
  
- Allow interval to be a floating-point value.
  
- Fix compatibility with psutil >= 2.0. [#10]
  
- Ensure that log file gets closed and plot gets drawn if process is interrupted. [#13]
  

## 0.1 (2013-12-17)

- Initial release
