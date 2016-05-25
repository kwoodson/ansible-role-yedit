Location for python unittests.

These should be run by sourcing the env-setup from the base of the yedit repository:
$ source test/env-setup

Since yedit is an ansible module it does not like to be run with unit tests.  To fix this:
$ vim roles/lib_yaml_editor/library/yedit.py

Then uncomment the if main section and comment out the bottom ansible import and the main() call.

Then navigate to the test/units/ directory.
$ python -m unittest yedit_tests
