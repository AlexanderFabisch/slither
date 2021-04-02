![slither](doc/source/_static/logo.png)

# Slither

A private replacement for online training logs.

![screenshot](doc/source/_static/slither.png)

## Install

    sudo pip install -r requirements.txt
    # install PyQt4 or PyQt5 + QtSvg + QtWebkit
    # e.g. (Ubuntu 16.04, Python 2.7):
    sudo apt-get install python-pyqt5 python-pyqt5.qtsvg python-pyqt5.qtwebkit
    sudo python setup.py install

Now you can start slither from the command line:

    slither

## Platforms

Slither has been tested with the following platforms:

* Ubuntu 20.10, Python 3.8
* Ubuntu 16.04, Python 2.7, 3.5
* Ubuntu 14.04, Python 2.7, 3.4
* Windows 8.1, Python 2.7

## Setup of Remote Data Repository

Slither allows you to set up your own server to share data among clients.
It will be used to share TCX files which can be uploaded and downloaded from
clients. **Note:** there is no support for https yet.

To initialize the remote repository, install slither on a server and start
the slither server:

    slither_server --datadir <directory> --port <port>

You have to enter a username and a password.

Now you can connect from any client with:

    slither --remote <url> --username <username> --password <password>

## Examples

Slither gives you full control over your data. All activities and all
GPS data are stored in a simple SQLite database. Take a look at the
[playground](https://github.com/AlexanderFabisch/slither/tree/master/playground)
if you need inspiration.

You can, for example, generate a heatmap from the trackpoints from your
GPS data. Here is an example from two weeks at Mallorca:

<img src="doc/source/_static/heatmap_mallorca.png" alt="Heatmap Mallorca" width="80%"/>

Here is the same data with additional (exaggerated) altitude information:

<img src="doc/source/_static/3d_mallorca.png" alt="3D Mallorca" width="80%"/>

Another idea for an application would be to check the overall training volume
before a running competition:

<img src="doc/source/_static/training_volume.png" alt="Training Volume" width="80%"/>

## Slither Core and IO

You don't have to use slither's GUI. `slither.core` and `slither.io` do not
depend on Qt or the domain model of slither. They are general purpose tools
to handle GPS and workout data. The following features are available:

* Data import from
    * GPS exchange format (GPX)
    * Flexible and Interoperable Data Transfer format (FIT)
    * Training Center XML format (TCX)
    * Polar's JSON format
* Data export to TCX
* Data analysis
    * Data cleaning and preprocessing
    * Distance and velocity computation from GPS trackpoints
    * Computation of records (fastest segments for given distances)
    * Computation of paces
    * Elevation statistics
* Visualization
    * Map rendering with Folium
    * Velocity histogram
    * Elevation profile
    * Plot of heartrate and speed over time

You can build the API documentation with `pdoc slither --html --skip-errors`
(requires [pdoc3](https://pdoc3.github.io/pdoc/)).
