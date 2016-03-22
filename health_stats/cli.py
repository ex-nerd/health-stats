
# Python 2 and 3
from __future__ import print_function

import sys
import argparse
# import textwrap
from pretty import pprint

from health_stats import HealthStats
from health_stats.parser import MySugrLogParser
from health_stats.config import Config

from health_stats.reports.text.glucose import glucose_summary
from health_stats.reports.graph.glucose import mean_glucose

def init():
    """
    Parse CLI arguments, then the config file, and return a populated config object
    """
    # Define and parse CLI args
    parser = argparse.ArgumentParser(
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        # description=textwrap.dedent(
        #     '''\
        #     required environment variables from /opt/rp/portal-cm/.aws/secrets.sh:
        #         AWS_ACCESS_KEY      Your personal AWS access key
        #         AWS_SECRET_KEY      Your personal AWS secret key
        #     '''
        # )
    )
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
    # Parse the config file
    Config.Initialize(args.config)


def parse():
    init()
    stats = HealthStats()
    for input_config in Config.inputs:
        for path in input_config.paths:
            print(path)
            parser = MySugrLogParser(Config.date_range)
            events = parser.parse_log(path)
            stats.extend(events)
    stats.analyze()

    glucose_summary(stats, 'out.txt')
    mean_glucose(stats, 'out.html')

    #for evt in stats.log.events:
    #    pprint(evt)
