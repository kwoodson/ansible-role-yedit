#!/usr/bin/env python
import sys
import os

# setup import path for yedit
sys.path.append(os.path.join(os.path.realpath('.'), '../library'))
import yedit


# perform simple test from README.md
yedit = yedit.Yedit('./pytest.yml')
results = yedit.put('a#b#c', {'d': {'e': {'f': "this is a test"}}})
print results
#yedit.write()
