#
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
The arg spec for the huawei_s_interfaces module
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class InterfacesArgs(object):

    def __init__(self, **kwargs):
        pass

    argument_spec = {'config': {'elements': 'dict',
                                'options': {'name': {'type': 'str', 'required': True},
                                            'description': {'type': 'str'},
                                            'enabled': {'default': True, 'type': 'bool'},
                                            'speed': {'type': 'str'},
                                            'mtu': {'type': 'int'},
                                            'duplex': {'type': 'str', 'choices': ['full', 'half']},
                                            'negotiation': {'type': 'bool'}},
                                'type': 'list'},
                     'state': {'choices': ['merged', 'replaced', 'overridden', 'deleted'],
                               'default': 'merged',
                               'type': 'str'}}
