# Release History

## Version 0.2

Not released yet.

### Features

* Loader for GPS exchange format (GPX).
* Loader for JSON files exported from Polar flow.
* It is now possible to specify a base path in which all data will be stored.

### Supported platforms

* Add support for PyQt5 in addition to PyQt4.

### Bugfixes

* Fix record computation for activities that contain
  NaN in velocities.
* Distances can be greater than 100 km now in the
  editor.

### Refactoring

* Remote data repository has a class as a public interface.
* Map rendering uses folium library.

## Version 0.1

2017/03/15

First public release. Support for Python 2.7 on Windows 8.1,
Python 2.7 and Python 3.4 on Ubuntu 14.04.
