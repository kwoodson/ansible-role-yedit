#!/usr/bin/env python
#     ___ ___ _  _ ___ ___    _ _____ ___ ___
#    / __| __| \| | __| _ \  /_\_   _| __|   \
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|

DOCUMENTATION='''
---
module: yedit
short_description: Create, modify, and idempotently manage yaml files.
description:
  - Modify yaml files programmatically.
options:
  state:
    description:
    - State represents whether to create, modify, delete, or list yaml
    required: true
    default: present
    choices: ["present", "absent", "list"]
    aliases: []
  debug:
    description:
    - Turn on debug information.
    required: false
    default: false
    aliases: []
  src:
    description:
    - The file that is the target of the modifications.
    required: false
    default: None
    aliases: []
  content:
    description:
    - Content represents the yaml content you desire to work with.  This could be the file contents to write or the inmemory data to modify.
    required: false
    default: None
    aliases: []
  content_type:
    description:
    - The python type of the content parameter.
    reqiured: false
    default: 'dict'
    aliases: []
  key:
    description:
    - The path to the value you wish to modify. Emtpy string means the top of the document.
    reqiured: false
    default: ''
    aliases: []
  value:
    description:
    - The incoming value of parameter 'key'.
    reqiured: false
    default:
    aliases: []
  value_type:
    description:
    - The python type of the incoming value.
    reqiured: false
    default: ''
    aliases: []
  update:
    description:
    - Whether the update should be performed on a dict/hash or list/array object.
    reqiured: false
    default: false
    aliases: []
  append:
    description:
    - Whether to append to an array/list.
    reqiured: false
    default: false
    aliases: []
  index:
    description:
    - Used in conjunction with the update parameter.  This will update a specific index in an array/list.
    reqiured: false
    default: false
    aliases: []
  curr_value:
    description:
    - Used in conjunction with the update parameter.  This is the current value of 'key' in the yaml file.
    reqiured: false
    default: false
    aliases: []
  curr_value_format:
    description:
    - Format of the incoming current value.
    choices: ["yaml", "json", "str"]
    reqiured: false
    default: false
    aliases: []
  backup:
    description:
    - Whether to make a backup copy of the current file when performing an edit.
    reqiured: false
    default: true
    aliases: []
  lock:
    description:
    - Lock the file to support multiple concurrent same yaml file modifications
    required: false
    default: false
    aliases: []
author:
- "Kenny Woodson <kwoodson@redhat.com>"
extends_documentation_fragment: []
'''

EXAMPLES = '''
# Simple insert of key, value
- name: insert simple key, value
  yedit:
    src: somefile.yml
    key: test
    value: somevalue
    state: present
# Results:
# test: somevalue

# Multilevel insert of key, value
- name: insert simple key, value
  yedit:
    src: somefile.yml
    key: a#b#c
    value: d
    state: present
# Results:
# a:
#   b:
#     c: d
'''


'''
module for managing yaml files
'''

import os
import re
import copy
import fcntl

import json
import yaml
# This is here because of a bug that causes yaml
# to incorrectly handle timezone info on timestamps
def timestamp_constructor(_, node):
    ''' return timestamps as strings'''
    return str(node.value)
yaml.add_constructor(u'tag:yaml.org,2002:timestamp', timestamp_constructor)


class YeditException(Exception):
    ''' Exception class for Yedit '''
    pass

class Yedit(object):
    ''' Class to modify yaml files '''
    re_valid_key = r"(((\[-?\d+\])|([0-9a-zA-Z-./_]+)).?)+$"
    re_key = r"(?:\[(-?\d+)\])|([0-9a-zA-Z-./_]+)"

    def __init__(self, filename=None, content=None, content_type='yaml', backup=False):
        self.content = content
        self.filename = filename
        self.__yaml_dict = content
        self.content_type = content_type
        self.backup = backup
        if self.filename and not self.content:
            if not self.load(content_type=self.content_type):
                self.__yaml_dict = {}

    @property
    def yaml_dict(self):
        ''' getter method for yaml_dict '''
        return self.__yaml_dict

    @yaml_dict.setter
    def yaml_dict(self, value):
        ''' setter method for yaml_dict '''
        self.__yaml_dict = value

    @staticmethod
    def remove_entry(data, key):
        ''' remove data at location key '''
        if key == '' and isinstance(data, dict):
            data.clear()
            return True
        elif key == '' and isinstance(data, list):
            del data[:]
            return True

        if not (key and re.match(Yedit.re_valid_key, key) and isinstance(data, (list, dict))):
            return None

        key_indexes = re.findall(Yedit.re_key, key)
        for arr_ind, dict_key in key_indexes[:-1]:
            if dict_key and isinstance(data, dict):
                data = data.get(dict_key, None)
            elif arr_ind and isinstance(data, list) and int(arr_ind) <= len(data) - 1:
                data = data[int(arr_ind)]
            else:
                return None

        # process last index for remove
        # expected list entry
        if key_indexes[-1][0]:
            if isinstance(data, list) and int(key_indexes[-1][0]) <= len(data) - 1:
                del data[int(key_indexes[-1][0])]
                return True

        # expected dict entry
        elif key_indexes[-1][1]:
            if isinstance(data, dict):
                del data[key_indexes[-1][1]]
                return True

    @staticmethod
    def add_entry(data, key, item=None):
        ''' Get an item from a dictionary with key notation a.b.c
            d = {'a': {'b': 'c'}}}
            key = a#b
            return c
        '''
        if key == '':
            pass
        elif not (key and re.match(Yedit.re_valid_key, key) and isinstance(data, (list, dict))):
            return None

        key_indexes = re.findall(Yedit.re_key, key)
        for arr_ind, dict_key in key_indexes[:-1]:
            if dict_key:
                if isinstance(data, dict) and data.has_key(dict_key) and data[dict_key]:
                    data = data[dict_key]
                    continue

                elif data and not isinstance(data, dict):
                    return None

                data[dict_key] = {}
                data = data[dict_key]

            elif arr_ind and isinstance(data, list) and int(arr_ind) <= len(data) - 1:
                data = data[int(arr_ind)]
            else:
                return None

        if key == '':
            data = item

        # process last index for add
        # expected list entry
        elif key_indexes[-1][0] and isinstance(data, list) and int(key_indexes[-1][0]) <= len(data) - 1:
            data[int(key_indexes[-1][0])] = item

        # expected dict entry
        elif key_indexes[-1][1] and isinstance(data, dict):
            data[key_indexes[-1][1]] = item

        return data

    @staticmethod
    def get_entry(data, key):
        ''' Get an item from a dictionary with key notation a.b.c
            d = {'a': {'b': 'c'}}}
            key = a.b
            return c
        '''
        if key == '':
            pass
        elif not (key and re.match(Yedit.re_valid_key, key) and isinstance(data, (list, dict))):
            return None

        key_indexes = re.findall(Yedit.re_key, key)
        for arr_ind, dict_key in key_indexes:
            if dict_key and isinstance(data, dict):
                data = data.get(dict_key, None)
            elif arr_ind and isinstance(data, list) and int(arr_ind) <= len(data) - 1:
                data = data[int(arr_ind)]
            else:
                return None

        return data

    def write(self):
        ''' write to file '''
        if not self.filename:
            raise YeditException('Please specify a filename.')

        if self.backup and self.file_exists():
            shutil.copy(self.filename, self.filename + '.orig')

        tmp_filename = self.filename + '.yedit'
        try:
            with open(tmp_filename, 'w') as yfd:
                yml_dump = yaml.safe_dump(self.yaml_dict, default_flow_style=False)
                for line in yml_dump.strip().split('\n'):
                    if '{{' in line and '}}' in line:
                        yfd.write(line.replace("'{{", '"{{').replace("}}'", '}}"') + '\n')
                    else:
                        yfd.write(line + '\n')
        except Exception as err:
            raise YeditException(err.message)

        os.rename(tmp_filename, self.filename)

        return (True, self.yaml_dict)

    def read(self):
        ''' write to file '''
        # check if it exists
        if not self.file_exists():
            return None

        contents = None
        with open(self.filename) as yfd:
            contents = yfd.read()

        return contents

    def file_exists(self):
        ''' return whether file exists '''
        if os.path.exists(self.filename):
            return True

        return False

    def load(self, content_type='yaml'):
        ''' return yaml file '''
        contents = self.read()

        if not contents:
            return None

        # check if it is yaml
        try:
            if content_type == 'yaml':
                self.yaml_dict = yaml.load(contents)
            elif content_type == 'json':
                self.yaml_dict = json.loads(contents)
        except yaml.YAMLError as err:
            # Error loading yaml or json
            YeditException('Problem with loading yaml file. %s' % err)

        return self.yaml_dict

    def get(self, key):
        ''' get a specified key'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, key)
        except KeyError as _:
            entry = None

        return entry

    def pop(self, path, key_or_item):
        ''' remove a key, value pair from a dict or an item for a list'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path)
        except KeyError as _:
            entry = None

        if entry == None:
            return  (False, self.yaml_dict)

        if isinstance(entry, dict):
            # pylint: disable=no-member,maybe-no-member
            if entry.has_key(key_or_item):
                entry.pop(key_or_item)
                return (True, self.yaml_dict)
            return (False, self.yaml_dict)

        elif isinstance(entry, list):
            # pylint: disable=no-member,maybe-no-member
            ind = None
            try:
                ind = entry.index(key_or_item)
            except ValueError:
                return (False, self.yaml_dict)

            entry.pop(ind)
            return (True, self.yaml_dict)

        return (False, self.yaml_dict)


    def delete(self, path):
        ''' remove path from a dict'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path)
        except KeyError as _:
            entry = None

        if entry == None:
            return  (False, self.yaml_dict)

        result = Yedit.remove_entry(self.yaml_dict, path)
        if not result:
            return (False, self.yaml_dict)

        return (True, self.yaml_dict)

    def exists(self, path, value):
        ''' check if value exists at path'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path)
        except KeyError as _:
            entry = None

        if isinstance(entry, list):
            if value in entry:
                return True
            return False

        elif isinstance(entry, dict):
            if isinstance(value, dict):
                rval = False
                for key, val  in value.items():
                    if  entry[key] != val:
                        rval = False
                        break
                else:
                    rval = True
                return rval

            return value in entry

        return entry == value

    def append(self, path, value):
        '''append value to a list'''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path)
        except KeyError as _:
            entry = None

        if entry == None or not isinstance(entry, list):
            return (False, self.yaml_dict)

        # pylint: disable=no-member,maybe-no-member
        entry.append(value)
        return (True, self.yaml_dict)

    def update(self, path, value, index=None, curr_value=None):
        ''' put path, value into a dict '''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path)
        except KeyError as _:
            entry = None

        if isinstance(entry, dict):
            # pylint: disable=no-member,maybe-no-member
            if not isinstance(value, dict):
                raise YeditException('Cannot replace key, value entry in dict with non-dict type.' \
                                     ' value=[%s]  [%s]' % (value, type(value)))

            entry.update(value)
            return (True, self.yaml_dict)

        elif isinstance(entry, list):
            # pylint: disable=no-member,maybe-no-member
            ind = None
            if curr_value:
                try:
                    ind = entry.index(curr_value)
                except ValueError:
                    return (False, self.yaml_dict)

            elif index != None:
                ind = index

            if ind != None and entry[ind] != value:
                entry[ind] = value
                return (True, self.yaml_dict)

            # see if it exists in the list
            try:
                ind = entry.index(value)
            except ValueError:
                # doesn't exist, append it
                entry.append(value)
                return (True, self.yaml_dict)

            #already exists, return
            if ind != None:
                return (False, self.yaml_dict)
        return (False, self.yaml_dict)

    def put(self, path, value):
        ''' put path, value into a dict '''
        try:
            entry = Yedit.get_entry(self.yaml_dict, path)
        except KeyError as _:
            entry = None

        if entry == value:
            return (False, self.yaml_dict)

        tmp_copy = copy.deepcopy(self.yaml_dict)
        result = Yedit.add_entry(tmp_copy, path, value)
        if not result:
            return (False, self.yaml_dict)

        self.yaml_dict = tmp_copy

        return (True, self.yaml_dict)

    def create(self, path, value):
        ''' create a yaml file '''
        if not self.file_exists():
            tmp_copy = copy.deepcopy(self.yaml_dict)
            result = Yedit.add_entry(tmp_copy, path, value)
            if result:
                self.yaml_dict = tmp_copy
                return (True, self.yaml_dict)

        return (False, self.yaml_dict)

def get_curr_value(invalue, val_type):
    '''return the current value'''
    if invalue == None:
        return None

    curr_value = None
    if val_type == 'yaml':
        curr_value = yaml.load(invalue)
    elif val_type == 'json':
        curr_value = json.loads(invalue)

    return curr_value

def parse_value(inc_value, vtype=''):
    '''determine value type passed'''
    true_bools = ['y', 'Y', 'yes', 'Yes', 'YES', 'true', 'True', 'TRUE', 'on', 'On', 'ON', ]
    false_bools = ['n', 'N', 'no', 'No', 'NO', 'false', 'False', 'FALSE', 'off', 'Off', 'OFF']

    # It came in as a string but you didn't specify value_type as string
    # we will convert to bool if it matches any of the above cases
    if isinstance(inc_value, str) and 'bool' in vtype:
        if inc_value not in true_bools and inc_value not in false_bools:
            raise YeditException('Not a boolean type. str=[%s] vtype=[%s]' % (inc_value, vtype))
    elif isinstance(inc_value, bool) and 'str' in vtype:
        inc_value = str(inc_value)

    # If vtype is not str then go ahead and attempt to yaml load it.
    if isinstance(inc_value, str) and 'str' not in vtype:
        try:
            inc_value = yaml.load(inc_value)
        except Exception as _:
            raise YeditException('Could not determine type of incoming value. value=[%s] vtype=[%s]' \
                                 % (type(inc_value), vtype))

    return inc_value

# pylint: disable=too-many-branches
def main():
    '''
    ansible oc module for secrets
    '''

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', type='str',
                       choices=['present', 'absent', 'list']),
            debug=dict(default=False, type='bool'),
            src=dict(default=None, type='str'),
            content=dict(default=None),
            content_type=dict(default='dict', choices=['dict', 'str']),
            key=dict(default='', type='str'),
            value=dict(),
            value_type=dict(default='', type='str'),
            update=dict(default=False, type='bool'),
            append=dict(default=False, type='bool'),
            index=dict(default=None, type='int'),
            curr_value=dict(default=None, type='str'),
            curr_value_format=dict(default='yaml', choices=['yaml', 'json', 'str'], type='str'),
            backup=dict(default=True, type='bool'),
            lock=dict(default=False, type='bool'),
        ),
        mutually_exclusive=[["curr_value", "index"], ['update', "append"]],
        required_one_of=[["content", "src"]],

        supports_check_mode=True,
    )
    state = module.params['state']

    yamlfile = Yedit(filename=module.params['src'], backup=module.params['backup'])

    if module.params['lock'] == True:
        lock_file = open(yamlfile.filename + ".yedit_lock", "w")
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

    if module.params['src']:
        rval = yamlfile.load()

        if yamlfile.yaml_dict == None and state != 'present':
            module.fail_json(msg='Error opening file [%s].  Verify that the' + \
                                 ' file exists, that it is has correct permissions, and is valid yaml.')

    if state == 'list':
        if module.params['key']:
            rval = yamlfile.get(module.params['key'])
        if rval == None:
            rval = {}
        module.exit_json(changed=False, results=rval, state="list")

    elif state == 'absent':
        if module.params['update']:
            rval = yamlfile.pop(module.params['key'], module.params['value'])
        else:
            rval = yamlfile.delete(module.params['key'])

        if rval[0]:
            yamlfile.write()

        module.exit_json(changed=rval[0], results=rval[1], state="absent")

    elif state == 'present':
        # check if content is different than what is in the file
        if module.params['content']:
            content = parse_value(module.params['content'], module.params['content_type'])

            # We had no edits to make and the contents are the same
            if yamlfile.yaml_dict == content and module.params['value'] == None:
                module.exit_json(changed=False, results=yamlfile.yaml_dict, state="present")

            yamlfile.yaml_dict = content

        # we were passed a value; parse it
        if module.params['value']:
            value = parse_value(module.params['value'], module.params['value_type'])
            key = module.params['key']
            if module.params['update']:
                curr_value = get_curr_value(parse_value(module.params['curr_value']),
                                            module.params['curr_value_format'])
                rval = yamlfile.update(key, value, index=module.params['index'], curr_value=curr_value)
            elif module.params['append']:
                rval = yamlfile.append(key, value)
            else:
                rval = yamlfile.put(key, value)

            if rval[0] and module.params['src']:
                yamlfile.write()

            module.exit_json(changed=rval[0], results=rval[1], state="present")

        # no edits to make
        if module.params['src']:
            rval = yamlfile.write()
            module.exit_json(changed=rval[0], results=rval[1], state="present")

        module.exit_json(changed=False, results=yamlfile.yaml_dict, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
# IF RUNNING UNIT TESTS, COMMENT OUT THIS SECTION
####
from ansible.module_utils.basic import *

main()
####
