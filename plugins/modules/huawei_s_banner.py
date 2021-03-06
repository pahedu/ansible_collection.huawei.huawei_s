#!/usr/bin/python
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: huawei_s_banner
version_added: "2.9"
author: "Aleksandr Natov (@pahedu)"
short_description: Manage multiline banners on Huawei S Series devices
description:
  - This will configure both login and motd banners on remote devices
    running Huawei VRP.  It allows playbooks to add or remote
    banner text from the active running configuration.
extends_documentation_fragment: huawei_s
notes:
  - Tested against VRP V200R010C00SPC600
options:
  banner:
    description:
      - Specifies which banner should be configured on the remote device.
    required: true
    choices: ['login', 'shell']
  text:
    description:
      - The banner text that should be
        present in the remote device running configuration.  This argument
        accepts a multiline string, with no empty lines. Requires I(state=present).
  state:
    description:
      - Specifies whether or not the configuration is
        present in the current devices active running configuration.
    default: present
    choices: ['present', 'absent']
"""
EXAMPLES = """
- name: configure the login banner
  huwei_s_banner:
    banner: login
    text: |
      this is my login banner
      that contains a multiline
      string
    state: present

- name: remove the motd banner
  huawei_s_banner:
    banner: shell
    state: absent

- name: Configure banner from file
  huawei_s_banner:
    banner:  shell
    text: "{{ lookup('file', './config_partial/raw_banner.cfg') }}"
    state: present

"""
RETURN = """
commands:
  description: The list of configuration mode commands to send to the device
  returned: always
  type: list
  sample:
    - banner login
    - this is my login banner
    - that contains a multiline
    - string
"""
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import exec_command
from ansible.module_utils.network.huawei_s.huawei_s import load_config
from ansible.module_utils.network.huawei_s.huawei_s import huawei_s_argument_spec, check_args
import re


def map_obj_to_commands(updates, module):
    commands = list()
    want, have = updates
    state = module.params['state']

    if state == 'absent' and 'text' in have.keys() and have['text']:
        commands.append('undo header %s' % module.params['banner'])

    elif state == 'present':
        if want['text'] and (want['text'] != have.get('text')):
            banner_cmd = 'header %s information' % module.params['banner']
            banner_cmd += ' "\n'
            banner_cmd += want['text'].strip()
            banner_cmd += '"'
            commands.append(banner_cmd)

    return commands


def map_config_to_obj(module):
    rc, out, err = exec_command(module,
                                'display current-configuration | begin header %s'
                                % module.params['banner'])
    if out:
        output = re.search(r'"(.*)"', out, re.S).group(1).strip()
        #replace artifacts from output to normal new line symbol
        output = output.replace('\u001b\u0019', '\n')
    else:
        output = None
    obj = {'banner': module.params['banner'], 'state': 'absent'}
    if output:
        obj['text'] = output
        obj['state'] = 'present'
    return obj


def map_params_to_obj(module):
    text = module.params['text']
    if text:
        text = str(text).strip()

    return {
        'banner': module.params['banner'],
        'text': text,
        'state': module.params['state']
    }


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        banner=dict(required=True, choices=['login', 'shell']),
        text=dict(),
        state=dict(default='present', choices=['present', 'absent'])
    )

    argument_spec.update(huawei_s_argument_spec)

    required_if = [('state', 'present', ('text',))]

    module = AnsibleModule(argument_spec=argument_spec,
                           required_if=required_if,
                           supports_check_mode=True)

    warnings = list()
    check_args(module, warnings)

    result = {'changed': False}
    if warnings:
        result['warnings'] = warnings
    want = map_params_to_obj(module)
    have = map_config_to_obj(module)

    commands = map_obj_to_commands((want, have), module)
    result['commands'] = commands

    if commands:
        if not module.check_mode:
            load_config(module, commands)

        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
