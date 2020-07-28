#! /usr/bin/env python3


from ansible.module_utils.basic import AnsibleModule as ansible
from pwd import getpwnam as user
import os


DOCUMENTATION = '''
---
module: faux_service
short_description: create a fake service for testing.
'''

EXAMPLES = '''
---
- name: Create an copy cat service named httpd
  faux_service:
    name: apache
    path: /tmp/apache
    owner: root
    mode: 0755
'''


def create_faux_service(data):

    name = data['name']
    path = data['path']
    mode = data['mode']
    owner = data['owner']

    is_error = False
    has_changed = False

    if not os.path.isdir(path):
        os.makedirs(path)

    path_and_file = "{0}/{1}".format(path, name)

    with open(path_and_file, 'w') as faux_service:
        faux_service.write('''
            #! /bin/bash
            FILENAME=$(basename $BASH_SOURCE)
            case "$1" in
            start)
                echo "Starting daemon"
                while [ 1 -lt 2 ]
                do
                logger "$FILENAME $0 running with parameters \"$@\""
                sleep 5
                done &
                ;;
            stop)
                echo "Stopping daemon"
                killall $FILENAME
                ;;
            esac
        ''')

    change_owner = "sudo chown -R {0} {1}".format(owner, path)
    os.system(change_owner)

    response = {
        "name": name,
        "path": path,
        "mode": mode,
        "owner": owner,
        }

    meta = {
        "status": "OK",
        "response": response}

    return is_error, has_changed, meta


def main():

    fields = {
        "name": {"required": True, "type": "str"},
        "path": {"required": True, "type": "str"},
        "mode": {"required": False, "type": "str"},
        "owner": {"required": False, "type": "str"}
    }

    module = ansible(argument_spec=fields)
    is_error, has_changed, result = create_faux_service(module.params)
    module.exit_json(changed=True, meta=module.params)

    if not is_error:
        module.exit_json(changed=has_changed, meta=result)
    else:
        module.fail_json(msg="Error creating faux service", meta=result)


if __name__ == '__main__':
    main()
