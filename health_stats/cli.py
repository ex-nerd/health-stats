
# Python 2 and 3
from __future__ import print_function

import sys
import argparse
from pretty import pprint

from health_stats import HealthStats
from health_stats.parser import MySugrLogParser
from health_stats.config import Config

from health_stats.reports import Reports


def init():
    """
    Parse CLI arguments, then the config file, and return a populated config object
    """
    # Define and parse CLI args
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbosity', action='count', help='Increase output verbosity.')
    parser.add_argument('-c', '--config', help='Path to config file.')
    (args, unknown_args) = parser.parse_known_args()
    # Alert the user about unknown arguments
    if (unknown_args):
        parser.print_help(sys.stderr)
        print(file=sys.stderr)
        for arg in unknown_args:
            print("Unrecognized argument: {0}".format(arg), file=sys.stderr)
        sys.exit(1)
    return args


def parse():
    # Initialize
    args = init()

    # Parse the config file
    Config.Initialize(args.config)

    # Parse the input files
    stats = HealthStats()
    for input_config in Config.inputs:
        for path in input_config.paths:
            print(path)
            parser = MySugrLogParser(Config.date_range)
            events = parser.parse_log(path)
            stats.extend(events)
    stats.analyze()

    # Make some output
    for report in Config.reports:
        r = report.report(stats)
        r.render(report.output)
