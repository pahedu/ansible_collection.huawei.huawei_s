#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The huawei_s_interfaces class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


from ansible.module_utils.network.common.cfg.base import ConfigBase
from ansible.module_utils.network.common.utils import to_list
from ansible.module_utils.network.huawei_s.facts.facts import Facts
from ansible.module_utils.network.huawei_s.utils.utils import get_interface_type, dict_to_set
from ansible.module_utils.network.huawei_s.utils.utils import remove_command_from_config_list, add_command_to_config_list
from ansible.module_utils.network.huawei_s.utils.utils import filter_dict_having_none_value, remove_duplicate_interface


class Interfaces(ConfigBase):
    """
    The huawei_s_interfaces class
    """

    gather_subset = [
        '!all',
        '!min',
    ]

    gather_network_resources = [
        'interfaces',
    ]

    params = ('description', 'mtu', 'speed', 'duplex', 'netgotiation')

    def __init__(self, module):
        super(Interfaces, self).__init__(module)

    def get_interfaces_facts(self):
        """ Get the 'facts' (the current configuration)

        :rtype: A dictionary
        :returns: The current configuration as a dictionary
        """
        facts, _warnings = Facts(self._module).get_facts(self.gather_subset, self.gather_network_resources)
        interfaces_facts = facts['ansible_network_resources'].get('interfaces')
        if not interfaces_facts:
            return []

        return interfaces_facts

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from moduel execution
        """
        result = {'changed': False}
        commands = list()
        warnings = list()

        existing_interfaces_facts = self.get_interfaces_facts()
        commands.extend(self.set_config(existing_interfaces_facts))
        #raise Exception(commands)
        if commands:
            if not self._module.check_mode:
                self._connection.edit_config(commands)
            result['changed'] = True
        result['commands'] = commands

        changed_interfaces_facts = self.get_interfaces_facts()

        result['before'] = existing_interfaces_facts
        if result['changed']:
            result['after'] = changed_interfaces_facts
        result['warnings'] = warnings

        return result

    def set_config(self, existing_interfaces_facts):
        """ Collect the configuration from the args passed to the module,
            collect the current configuration (as a dict from facts)

        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the deisred configuration
        """
        want = self._module.params['config']
        have = existing_interfaces_facts
        resp = self.set_state(want, have)
        return to_list(resp)

    def set_state(self, want, have):
        """ Select the appropriate function based on the state provided

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the deisred configuration
        """
        commands = []

        state = self._module.params['state']
        if state in ('overridden', 'merged', 'replaced') and not want:
            self._module.fail_json(msg='value of config parameter must not be empty for state {0}'.format(state))

        if state == 'overridden':
            commands = self._state_overridden(want, have)
        elif state == 'deleted':
            commands = self._state_deleted(want, have)
        elif state == 'merged':
            commands = self._state_merged(want, have)
        elif state == 'replaced':
            commands = self._state_replaced(want, have)

        return commands

    def _state_replaced(self, want, have):
        """ The command generator when state is replaced

        :param want: the desired configuration as a dictionary
        :param have: the current configuration as a dictionary
        :param interface_type: interface type
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the deisred configuration
        """
        commands = []

        for interface in want:
            for each in have:
                if each['name'] == interface['name']:
                    break
                elif interface['name'] in each['name']:
                    break
            else:
                continue
            have_dict = filter_dict_having_none_value(interface, each)
            want = dict()
            commands.extend(self._clear_config(want, have_dict))
            commands.extend(self._set_config(interface, each))
        # Remove the duplicate interface call
        commands = remove_duplicate_interface(commands)

        return commands

    def _state_overridden(self, want, have):
        """ The command generator when state is overridden

        :param want: the desired configuration as a dictionary
        :param obj_in_have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to migrate the current configuration
                  to the desired configuration
        """
        commands = []

        for each in have:
            for interface in want:
                if each['name'] == interface['name']:
                    break
            else:
                # We didn't find a matching desired state, which means we can
                # pretend we recieved an empty desired state.
                interface = dict(name=each['name'])
                commands.extend(self._clear_config(interface, each))
                continue

            commands.extend(self._clear_config(interface, each))
            commands.extend(self._set_config(interface, each))

        # Remove the duplicate interface call
        #commands = remove_duplicate_interface(commands)
        #raise Exception(commands)
        return commands

    def _state_merged(self, want, have):
        """ The command generator when state is merged

        :param want: the additive configuration as a dictionary
        :param obj_in_have: the current configuration as a dictionary
        :rtype: A list
        :returns: the commands necessary to merge the provided into
                  the current configuration
        """
        commands = []

        for interface in want:
            for each in have:
                if each['name'] == interface['name']:
                    break
            else:
                continue
            commands.extend(self._set_config(interface, each))

        return commands

    def _state_deleted(self, want, have):
        """ The command generator when state is deleted

        :param want: the objects from which the configuration should be removed
        :param obj_in_have: the current configuration as a dictionary
        :param interface_type: interface type
        :rtype: A list
        :returns: the commands necessary to remove the current configuration
                  of the provided objects
        """
        commands = []

        if want:
            for interface in want:
                for each in have:
                    if each['name'] == interface['name']:
                        break
                else:
                    continue
                interface = dict(name=interface['name'])
                commands.extend(self._clear_config(interface, each))
        else:
            for each in have:
                want = dict()
                commands.extend(self._clear_config(want, each))
        return commands

    def _set_config(self, want, have):
        # Set the interface config based on the want and have config
        commands = []
        interface = 'interface ' + want['name']
        interface_type = get_interface_type(want['name'])

        # Get the diff b/w want and have
        want_dict = dict_to_set(want)
        have_dict = dict_to_set(have)
        diff = want_dict - have_dict

        if diff:
            diff = dict(diff)
            if diff.get('description'):
                cmd = 'description {0}'.format(want.get('description'))
                add_command_to_config_list(interface, cmd, commands)
            if diff.get('mtu'):
                cmd = 'jumboframe enable {0}'.format(want.get('mtu'))
                add_command_to_config_list(interface, cmd, commands)
            if diff.get('enabled'):
                add_command_to_config_list(interface, 'undo shutdown', commands)
            elif diff.get('enabled') is False:
                add_command_to_config_list(interface, 'shutdown', commands)
            if diff.get('negotiation'):
                add_command_to_config_list(interface, 'negotiation auto', commands)
            if interface_type.lower() == 'gigabitethernet' and not diff.get('negotiation'):
                for item in diff.keys():
                    if item in ['speed', 'duplex']:
                        cmd = 'undo negotiation auto'
                        add_command_to_config_list(interface, cmd, commands)
                        break
                if diff.get('speed') == '1000' and have.get('duplex') == 'half':
                    cmd = 'duplex full'
                    add_command_to_config_list(interface, cmd, commands)
                    cmd = 'speed {0}'.format(want.get('speed'))
                    add_command_to_config_list(interface, cmd, commands)
                elif diff.get('speed'):
                    cmd = 'speed {0}'.format(want.get('speed'))
                    add_command_to_config_list(interface, cmd, commands)
                if diff.get('duplex'):
                    cmd = 'duplex {0}'.format(want.get('duplex'))
                    add_command_to_config_list(interface, cmd, commands)
            add_command_to_config_list(interface, 'quit', commands)

        return commands

    def _clear_config(self, want, have):
        # Delete the interface config based on the want and have config
        commands = []
        change_flag = False

        if want.get('name'):
            interface_type = get_interface_type(want['name'])
            interface = 'interface ' + want['name']
        else:
            interface_type = get_interface_type(have['name'])
            interface = 'interface ' + have['name']

        if have.get('description') and want.get('description') != have.get('description'):
            remove_command_from_config_list(interface, 'description', commands)
            change_flag = True
        if not have.get('enabled') and want.get('enabled') != have.get('enabled'):
            # if enable is False set enable as True which is the default behavior
            remove_command_from_config_list(interface, 'shutdown', commands)
            change_flag = True
        if have.get('mtu') and want.get('mtu') != have.get('mtu'):
            remove_command_from_config_list(interface, 'jumboframe enable', commands)
            change_flag = True

        if interface_type.lower() == 'gigabitethernet':
            if have.get('speed') and want.get('speed') != have.get('speed') and not have.get('negotiation'):
                remove_command_from_config_list(interface, 'speed', commands)
                change_flag = True
            if have.get('duplex') and want.get('duplex') != have.get('duplex') and not have.get('negotiation'):
                remove_command_from_config_list(interface, 'duplex', commands)
                change_flag = True
            if not have.get('negotiation') and want.get('negotiation') != have.get('negotiation'):
                remove_command_from_config_list(interface, 'speed', commands)
                remove_command_from_config_list(interface, 'duplex', commands)
                add_command_to_config_list(interface, 'negotiation auto', commands)
                change_flag = True
        if change_flag:
            add_command_to_config_list(interface, 'quit', commands)

        return commands