#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Ansible by Red Hat, inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = """
---
module: huawei_s_lldp
version_added: "2.9"
author: "Aleksandr Natov (@pahedu)"
short_description: Manage LLDP configuration on Huawei S Series network devices.
description:
  - This module provides declarative management of LLDP service
    on Huawei S Series network devices.
notes:
  - Tested against  VRP V200R010C00SPC600
options:
  state:
    description:
      - State of the LLDP configuration. If value is I(present) lldp will be enabled
        else if it is I(absent) it will be disabled.
    default: present
    choices: ['present', 'absent']
extends_documentation_fragment: huawei_s
"""

EXAMPLES = """
- name: Enable LLDP service
  huawei_s_lldp:
    state: present

- name: Disable LLDP service
  huawei_s_lldp:
    state: absent
"""

RETURN = """
commands:
  description: The list of configuration mode commands to send to the device
  returned: always, except for the platforms that use Netconf transport to manage the device.
  type: list
  sample:
    - lldp enable
"""
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.huawei_s.huawei_s import load_config, run_commands
from ansible.module_utils.network.huawei_s.huawei_s import huawei_s_argument_spec


def has_lldp(module):
    output = run_commands(module, ['display lldp local | include LLDP Status'])

    is_lldp_enable = False
    match = re.search(r'LLDP Status\s+:\s*(\S+)', output[0])
    if match:
        if match.group(1) == 'enabled':
            is_lldp_enable = True

    return is_lldp_enable


def main():
    """ main entry point for module execution
    """
    argument_spec = dict(
        state=dict(default='present',
                   choices=['present', 'absent',
                            'enabled', 'disabled'])
    )

    argument_spec.update(huawei_s_argument_spec)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    warnings = list()

    result = {'changed': False}

    if warnings:
        result['warnings'] = warnings

    HAS_LLDP = has_lldp(module)

    commands = []

    if module.params['state'] == 'absent' and HAS_LLDP:
        commands.append('undo lldp enable')
    elif module.params['state'] == 'present' and not HAS_LLDP:
        commands.append('lldp enable')

    result['commands'] = commands

    if commands:
        if not module.check_mode:
            load_config(module, commands)

        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
