#pylint: skip-file

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
    if isinstance(inc_value, str) and 'str' not in vtype:
        if inc_value in true_bools:
            return True
        elif inc_value in false_bools:
            return False

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
            src=dict(default=None, required=True, type='str'),
            content=dict(default=None),
            content_type=dict(default='dict', choices=['dict', 'str']),
            key=dict(default=None, type='str'),
            value=dict(),
            value_type=dict(default='', type='str'),
            update=dict(default=False, type='bool'),
            append=dict(default=False, type='bool'),
            index=dict(default=None, type='int'),
            curr_value=dict(default=None, type='str'),
            curr_value_format=dict(default='yaml', choices=['yaml', 'json', 'str'], type='str'),
            backup=dict(default=True, type='bool'),
        ),
        mutually_exclusive=[["curr_value", "index"], ["content", "value"], ['update', "append"]],

        supports_check_mode=True,
    )
    state = module.params['state']

    yamlfile = Yedit(module.params['src'], backup=module.params['backup'])

    rval = yamlfile.load()
    if not rval and state != 'present':
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

    elif state == 'present' and module.params['value'] != None:

        value = parse_value(module.params['value'], module.params['value_type'])

        if rval != None:
            if module.params['update']:
                curr_value = get_curr_value(parse_value(module.params['curr_value']),
                                            module.params['curr_value_format'])
                rval = yamlfile.update(module.params['key'], value, index=module.params['index'], curr_value=curr_value)
            elif module.params['append']:
                rval = yamlfile.append(module.params['key'], value)
            else:
                rval = yamlfile.put(module.params['key'], value)

            if rval[0]:
                yamlfile.write()
            module.exit_json(changed=rval[0], results=rval[1], state="present")

        rval = yamlfile.put(module.params['key'], value)
        rval = yamlfile.write()
        module.exit_json(changed=rval[0], results=rval[1], state="present")

    elif state == 'present' and module.params['content'] != None:
        content = None
        if module.params['content_type'] == 'dict':
            content = module.params['content']
        elif module.params['content_type'] == 'str':
            content = yaml.load(module.params['content'])

        if yamlfile.yaml_dict == content:
            module.exit_json(changed=False, results=yamlfile.yaml_dict, state="present")

        yamlfile.yaml_dict = content
        rval = yamlfile.write()
        module.exit_json(changed=rval[0], results=rval[1], state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# If running unit tests, please uncomment this block
####
#if __name__ == '__main__':
    #from ansible.module_utils.basic import *
    #main()
####


# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
# IF RUNNING UNIT TESTS, COMMENT OUT THIS SECTION
####
from ansible.module_utils.basic import *

main()
####
