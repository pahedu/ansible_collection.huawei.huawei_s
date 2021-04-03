#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the resource
#   module builder playbook.
#
# Do not edit this file manually.
#
# Changes to this file will be over written
#   by the resource module builder.
#
# Changes should be made in the model used to
#   generate this file or in the resource module
#   builder template.
#
#############################################

"""
The module file for huawei_s_lldp_global
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = """
---
module: huawei_s_lldp_global
version_added: 2.9
short_description: Configure and manage Link Layer Discovery Protocol(LLDP) attributes on Huawei S Series platforms.
description: This module configures and manages the Link Layer Discovery Protocol(LLDP) attributes on Huawei S Series platforms.
author: Sumit Jaiswal (@justjais)
notes:
  - Tested against VRP V200R010C00SPC600
  - This module works with connection C(network_cli),
options:
  config:
    description: A dictionary of LLDP options
    type: dict
    suboptions:
      holdtime:
        description:
          - LLDP holdtime (in multipliers) to be sent in packets.
          - Refer to vendor documentation for valid values.
        type: int
      reinit:
        description:
          - Specify the delay (in secs) for LLDP to initialize.
          - Refer to vendor documentation for valid values.
          - NOTE, if LLDP reinit is configured with a starting
            value, idempotency won't be maintained as the Huawei
            device doesn't record the starting reinit configured
            value. As such, Ansible cannot verify if the respective
            starting reinit value is already configured or not from
            the device side. If you try to apply starting reinit
            value in every play run, Ansible will show changed as True.
            For any other reinit value, idempotency will be maintained
            since any other reinit value is recorded in the Huawei device.
        type: int
      enabled:
        description:
          - Enable LLDP
        type: bool
      timer:
        description:
          - Specify the rate at which LLDP packets are sent (in sec).
          - Refer to vendor documentation for valid values.
        type: int
  state:
    description:
    - The state of the configuration after module completion
    type: str
    choices:
    - merged
    - replaced
    - deleted
    default: merged
"""

EXAMPLES = """
---

# Using merged

# Before state:
# -------------
#[HUAWEI]display lldp local
#Info: Global LLDP is not enabled.

- name: Merge provided configuration with device configuration
  huawei_s_lldp_global:
    config:
      holdtime_multiplier: 2
      enabled: True
      reinit: 3
      timer: 10
    state: merged

# After state:
# ------------
#[HUAWEI]display lldp local
#System configuration
#--------------------------------------------------------------------------
#LLDP Status                     :enabled             (default is disabled)
#LLDP Message Tx Interval        :10                  (default is 30s)
#LLDP Message Tx Hold Multiplier :2                   (default is 4)
#LLDP Refresh Delay              :3                   (default is 2s)
#LLDP Tx Delay                   :2                   (default is 2s)
#LLDP Notification Interval      :5                   (default is 5s)
#LLDP Notification Enable        :enabled             (default is enabled)



# Using replaced

#[HUAWEI]display lldp local
#System configuration
#--------------------------------------------------------------------------
#LLDP Status                     :enabled             (default is disabled)
#LLDP Message Tx Interval        :10                  (default is 30s)
#LLDP Message Tx Hold Multiplier :2                   (default is 4)
#LLDP Refresh Delay              :3                   (default is 2s)
#LLDP Tx Delay                   :2                   (default is 2s)
#LLDP Notification Interval      :5                   (default is 5s)
#LLDP Notification Enable        :enabled             (default is enabled)


- name: Replaces LLDP device configuration with provided configuration
  huawei_s_lldp_global:
    config:
      holdtime_multiplier: 3
      reinit: 5
    state: replaced

# After state:
# -------------
#[HUAWEI]display lldp local
#Info: Global LLDP is not enabled.


# Using Deleted without any config passed
#"(NOTE: This will delete all of configured LLDP module attributes)"

# Before state:
# -------------
#[HUAWEI]display lldp local
#System configuration
#--------------------------------------------------------------------------
#LLDP Status                     :enabled             (default is disabled)
#LLDP Message Tx Interval        :10                  (default is 30s)
#LLDP Message Tx Hold Multiplier :2                   (default is 4)
#LLDP Refresh Delay              :3                   (default is 2s)
#LLDP Tx Delay                   :2                   (default is 2s)
#LLDP Notification Interval      :5                   (default is 5s)
#LLDP Notification Enable        :enabled             (default is enabled)


- name: "Delete LLDP attributes (Note: This won't delete the interface itself)"
  huawei_s_lldp_global:
    state: deleted

# After state:
# -------------
#[HUAWEI]display lldp local
#Info: Global LLDP is not enabled.

"""

RETURN = """
before:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: dict
  sample: The configuration returned will always be in the same format of the parameters above.
after:
  description: The configuration as structured data after module completion.
  returned: when changed
  type: dict
  sample: The configuration returned will always be in the same format of the parameters above.
commands:
  description: The set of commands pushed to the remote device
  returned: always
  type: list
  sample: ['lldp message-transmission hold-multiplier 2', 'lldp enable', 'lldp message-transmission interval 10']
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.ios.argspec.lldp_global.lldp_global import Lldp_globalArgs
from ansible.module_utils.network.ios.config.lldp_global.lldp_global import Lldp_global


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    required_if = [('state', 'merged', ('config',)),
                   ('state', 'replaced', ('config',))]

    module = AnsibleModule(argument_spec=Lldp_globalArgs.argument_spec,
                           required_if=required_if,
                           supports_check_mode=True)

    result = Lldp_global(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
