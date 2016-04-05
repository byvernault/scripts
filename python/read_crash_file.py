#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, gzip, pickle

if len(sys.argv) == 0:
    print 'Please provide the .pklz file to read'
else:
    f = pickle.load(gzip.open(sys.argv[0], 'rb'))
    print f
