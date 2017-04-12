
# Python 2 and 3
from __future__ import print_function

import os
import sys
import datetime
import argparse
from pretty import pprint

from health_stats.parsers import Parsers
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

    # Parse the input files into the database
    inputs_found = 0
    for input_config in Config.inputs:
        parser_class = Parsers[input_config.format]
        for path in input_config.paths:
            print("parsing: {}".format(path))
            parser = parser_class(Config.date_range)
            parser.parse_log(path)
            inputs_found += 1
            if input_config.archive:
                if not os.path.exists(input_config.archive):
                    os.makedirs(input_config.archive)
                new_path = os.path.join(input_config.archive, '{}-{}'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'), os.path.basename(path)))
                print("archiving to: {}".format(new_path))
                os.rename(path, new_path)

    # Make some output
    for report in Config.reports:
        r = report.report(
            start=report.date_range.start,
            end=report.date_range.end,
        )
        r.render(report.output)

    # Exit, but only report success if we actually imported new data
    sys.exit(0 if inputs_found else 1)
