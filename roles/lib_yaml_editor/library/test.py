#!/usr/bin/env python
import yedit

yedit = yedit.Yedit('/tmp/pytest.yml')
results = yedit.put('a#b#c[0]#d', {'e': {'f': "this is a test"}})
#results = yedit.put('a#b#c', {'d': {'e': {'f': "this is a test"}}})
print results
#yedit.write()

