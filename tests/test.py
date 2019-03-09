#!/usr/bin/env python
import os
import sys

# setup import path for yedit
sys.path.append(os.path.join(os.path.realpath('.'), '../library'))
import yedit  # noqa: F402


# perform simple test from README.md
yedit = yedit.Yedit('./pytest.yml')
results = yedit.put('a#b#c', {'d': {'e': {'f': "this is a test"}}})
print(results)
# yedit.write()
