#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The huawei_s lacp fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import re
from copy import deepcopy
from ansible.module_utils.network.common import utils
from ansible.module_utils.network.huawei_s.argspec.lacp.lacp import LacpArgs


class LacpFacts(object):
    """ The huawei_s lacp fact class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = LacpArgs.argument_spec
        spec = deepcopy(self.argument_spec)
        if subspec:
            if options:
                facts_argument_spec = spec[subspec][options]
            else:
                facts_argument_spec = spec[subspec]
        else:
            facts_argument_spec = spec

        self.generated_spec = utils.generate_dict(facts_argument_spec)

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for lacp
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if connection:
            pass

        if not data:
            data = connection.get('display lacp brief')

        obj = {}
        if data:
            lacp_obj = self.render_config(self.generated_spec, data)
            if lacp_obj:
                obj = lacp_obj

        ansible_facts['ansible_network_resources'].pop('lacp', None)
        facts = {}

        params = utils.validate_config(self.argument_spec, {'config': obj})
        facts['lacp'] = utils.remove_empties(params['config'])
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts

    def render_config(self, spec, conf):
        """
        Render config as dictionary structure and delete keys
          from spec for null values

        :param spec: The facts tree, generated from the argspec
        :param conf: The configuration
        :rtype: dictionary
        :returns: The generated config
        """
        config = deepcopy(spec)

        match = re.search(r'System Priority\s*:\s+(\d+)', conf)
        if match:
            config['system']['priority'] = int(match.group(1))
        match = re.search(r'System ID\s*:\s+(\S+)', conf)
        if match:
            config['system']['id'] = match.group(1)

        return utils.remove_empties(config)