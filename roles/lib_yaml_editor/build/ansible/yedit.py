#pylint: skip-file

def get_curr_value(invalue, val_type):
    '''return the current value'''
    if not invalue:
        return None

    curr_value = None
    if val_type == 'yaml':
        curr_value = yaml.load(invalue)
    elif val_type == 'json':
        curr_value = json.loads(invalue)

    return curr_value

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
            content=dict(default=None, type='dict'),
            key=dict(default=None, type='str'),
            value=dict(),
            update=dict(default=False, type='bool'),
            index=dict(default=None, type='int'),
            curr_value=dict(default=None, type='str'),
            curr_value_format=dict(default='yaml', choices=['yaml', 'json'], type='str'),
        ),
        mutually_exclusive=[["curr_value", "index"]],

        supports_check_mode=True,
    )
    state = module.params['state']

    yamlfile = Yedit(module.params['src'], module.params['content'])

    rval = yamlfile.load()
    if not rval and state != 'present':
        module.fail_json(msg='Error opening file [%s].  Verify that the' + \
                             ' file exists, that it is has correct permissions, and is valid yaml.')

    if state == 'list':
        if module.params['key']:
            rval = yamlfile.get(module.params['key'])
        module.exit_json(changed=False, results=rval, state="list")

    if state == 'absent':
        rval = yamlfile.delete(module.params['key'])
        module.exit_json(changed=rval[0], results=rval[1], state="absent")

    if state == 'present':

        value = module.params['value']

        if rval:
            if module.params['update']:
                curr_value = get_curr_value(module.params['curr_value'], module.params['curr_value_format'])
                rval = yamlfile.update(module.params['key'], value, index=module.params['index'], curr_value=curr_value)
            else:
                rval = yamlfile.put(module.params['key'], value)

            if rval[0]:
                yamlfile.write()
            module.exit_json(changed=rval[0], results=rval[1], state="present")

        if not module.params['content']:
            rval = yamlfile.put(module.params['key'], value)
        else:
            rval = yamlfile.load()
        yamlfile.write()

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
