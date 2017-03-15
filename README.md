# Slither

A private replacement for online training logs.

![screenshot](slither.png)

## Install

    sudo pip install -r requirements.txt
    # install PyQt4
    sudo python setup.py install

Now you can start slither from the command line:

    slither

## Platforms

Slither has been tested with the following platforms:

* Ubuntu 14.04, Python 2.7
* Ubuntu 14.04, Python 3.4
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
