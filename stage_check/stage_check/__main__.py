#!/usr/bin/env python36
"""
"""
import sys

import argparse

# import stage_check
#   - works if importing stage_check/stage_check.py outside
#     the context of a wheel package names stage_check
# from stage_check import stage_check
#   - works if importing stage_check/stage_check.py from
#     the context of a wheel package names stage_check,
#     but not from outside..
#   
# renaming stage_check.py -> test_framwork.py works in
# both contexts...
#
try:
    from stage_check import stage_check
except ImportError:
    import stage_check

def parse_command_args():
    parser = argparse.ArgumentParser(description='Run Stage Tests')

    parser.add_argument('-r', '--router',
                        default='',
                        help='Effective router name')

    parser.add_argument('-n', '--node',
                        default='',
                        help='Effective node name')

    parser.add_argument('-p', '--primary-regex',
                        default='^.*?A$',
                        help='Regex to identify primary node')

    parser.add_argument('-s', '--secondary-regex',
                        default='^.*?B$',
                        help='Regex to identify secondary node')

    parser.add_argument('--site-regex',
                        default='([0-9]+)',
                        help='Regex to extract a router/node site number; '
                        'site number must be a regex group -- enclosed by ()s')

    parser.add_argument('--pod-regex',
                        default='[pP]([0-9]+)$',
                        help='Regex to extract a router/node pod number; '
                        'pod number must be a regex group -- enclosed by ()s')

    parser.add_argument('-v', '--version', action='store_true',
                       default=False, help='Print version Information')

    parser.add_argument('-d', '--debug', action='store_true',
                       default=False, help='Outputs debug information')

    parser.add_argument('-e', '--exclude', nargs='+',
                       default=[], help='Excludes one or more tests')

    parser.add_argument('--context', action='store_true',
                       default=False, help='Outputs router context(s)')

    parser.add_argument('--warn-is-fail', action='store_true',
                       default=False, help='Treat warning as failure')

    parser.add_argument('-R', '--router-patterns', nargs='+',
                       default=[], help='Conductor only: router substring matching patterns')

    parser.add_argument('--regex-patterns', action='store_true',
                       default=False, help='Conductor only: match router patterns with regex')

    parser.add_argument('--start-after',
                        default=None,
                        help='Conductor only: Skip routers matching pattern until after this substring match')

    parser.add_argument('-o', '--output',
                        default='',
                        help='Send output to filename provided')

    parser.add_argument('-c', '--config-path', 
                       default=None, 
                       help='Path for configuration file')

    parser.add_argument('-g', '--generic', action='store_true',
                       default=False, help='Use the generic config provided in the stage_check pex file.' + 
                       'If the --config-path (-c) option is also provided, it will be preferred' )

    parser.add_argument('-j', '--json', action='store_true',
                        default=False, help='Override configuration to output as JSON')    
 
    return parser.parse_args()

############################
#
#
# Main Section
#
############################
def main():
    args = parse_command_args()
    te = stage_check.TestExecutor(args)
    te.test_routers()
    return te.tests_shell_status()

if __name__ == '__main__':
     status =  main()
     sys.exit(status)
