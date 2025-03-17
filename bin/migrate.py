#!/usr/bin/env python

import pathlib
import sys

rootdir = pathlib.Path(__file__).parent.parent
sys.path.append(str(rootdir))

import somisana_migrate.systemdata
import odp.logfile

if __name__ == '__main__':
    odp.logfile.initialize()
    somisana_migrate.systemdata.initialize()
