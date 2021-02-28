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

* Ubuntu 14.04, Python 2.7, 3.4
* Ubuntu 16.04, Python 2.7, 3.5
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

![Heatmap Mallorca](doc/source/_static/heatmap_mallorca.png)

Here is the same data with additional (exaggerated) altitude information:

![3D Mallorca](doc/source/_static/3d_mallorca.png)

Another idea for an application would be to check the overall training volume
before a running competition:

![Training Volume](doc/source/_static/training_volume.png)
