#!/usr/bin/env python3
#
# Copyright 2018-2019, Data61
# Commonwealth Scientific and Industrial Research Organisation (CSIRO)
# ABN 41 687 119 230.
#
# This software may be distributed and modified according to the terms of
# the GNU General Public License version 2. Note that NO WARRANTY is provided.
# See "LICENSE_GPLv2.txt" for details.
#
# @TAG(DATA61_GPL)
#

from __future__ import print_function, division
import argparse
import logging
import yaml

from hardware import config, fdt
from hardware.outputs import c_header, compat_strings, yaml as yaml_out
from hardware.utils.rule import HardwareYaml

OUTPUTS = {
    'c_header': c_header,
    'compat_strings': compat_strings,
    'yaml': yaml_out,
}


def validate_rules(rules, schema):
    ''' Try and validate a hardware rules file against a schema.
        If jsonschema is not installed, succeed with a warning. '''
    try:
        from jsonschema import validate
        return validate(rules, schema)
    except ImportError:
        logging.warning('Skipping hardware YAML validation; `pip install jsonschema` to validate')
        return True


def add_task_args(outputs: dict, parser: argparse.ArgumentParser):
    ''' Add arguments for each output type. '''
    for t in sorted(outputs.keys()):
        task = outputs[t]
        name = t.replace('_', '-')
        group = parser.add_argument_group('{} pass'.format(name))
        group.add_argument('--' + name, help=task.__doc__.strip(), action='store_true')
        task.add_args(group)


def main(args: argparse.Namespace):
    ''' Parse the DT and hardware config YAML and run each
    selected output method. '''
    cfg = config.get_arch_config(args.arch, args.addrspace_max)
    parsed_dt = fdt.FdtParser(args.dtb)
    rules = yaml.load(args.hardware_config, Loader=yaml.FullLoader)
    schema = yaml.load(args.hardware_schema, Loader=yaml.FullLoader)
    validate_rules(rules, schema)
    hardware = HardwareYaml(rules, cfg)

    arg_dict = vars(args)
    for t in sorted(OUTPUTS.keys()):
        if arg_dict[t]:
            OUTPUTS[t].run(parsed_dt, hardware, cfg, args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='transform device tree input to seL4 build configuration artefacts'
    )

    parser.add_argument('--dtb', help='device tree blob to parse for generation',
                        required=True, type=argparse.FileType('rb'))
    parser.add_argument('--hardware-config', help='YAML file containing configuration for kernel devices',
                        required=True, type=argparse.FileType('r'))
    parser.add_argument('--hardware-schema', help='YAML file containing schema for hardware config',
                        required=True, type=argparse.FileType('r'))
    parser.add_argument('--arch', help='architecture to generate for', default='arm')
    parser.add_argument('--addrspace-max',
                        help='maximum address that is available as device untyped', type=int, default=32)

    parser.add_argument('--enable-profiling', help='enable profiling',
                        action='store_const', const=True, default=False)

    add_task_args(OUTPUTS, parser)

    args = parser.parse_args()

    if args.enable_profiling:
        import cProfile
        cProfile.run('main(args)', sort='cumtime')
    else:
        main(args)
