
# Python 2 and 3
from __future__ import print_function

import os
import sys
import yaml

from collections import namedtuple

from pretty import pprint

import glob

from health_stats.date_range import DateRange

from health_stats.parsers import Parsers
from health_stats.reports import Reports


class ConfigData(object):
    """
    Singleton class to hold global config data

    @see http://python-3-patterns-idioms-test.readthedocs.org/en/latest/Singleton.html
    """

    __InputConfig = namedtuple('InputConfig', ['format', 'tz', 'archive', 'paths'])
    __ReportConfig = namedtuple('ReportConfig', ['report', 'output', 'date_range'])

    class __ConfigData(object):

        __slots__ = (
            'date_range',
            'inputs',
            'reports',
        )

        def Initialize(self, path):
            if not path:
                path = os.path.expanduser("~/.health_stats/config.yml")
            with open(path, 'rb') as file:
                try:
                    conf = yaml.load(file)
                except yaml.YAMLError as err:
                    print(err, file=sys.stderr)
                    exit(1)

            # Parse the configured date_rage
            if 'date_range' not in conf:
                raise ValueError('Missing date_range section in config file: {}'.format(path))
            self.date_range = DateRange(
                start=conf['date_range'].get('start'),
                end=conf['date_range'].get('end'),
                tz=conf['date_range'].get('tz'),
            )

            # The list of input files
            if 'inputs' not in conf:
                raise ValueError('Missing inputs section in config file: {}'.format(path))
            self.inputs = []
            for input in conf['inputs']:
                # Known inputs?
                input['format'] = input['format'].lower()
                if input['format'] not in Parsers:
                    raise ValueError('Unrecognized input file format: {} not in {}'.format(input['format'], Parsers))
                # Expand and parse the list of input files
                found_paths = []
                for path in input['paths']:
                    found_paths.extend(glob.glob(os.path.expanduser(path)))
                if len(found_paths) > 0:
                    input['paths'] = found_paths
                    self.inputs.append(ConfigData.__InputConfig(
                        format=input['format'],
                        tz=input['tz'],
                        archive=os.path.expanduser(input['archive']) if 'archive' in input else None,
                        paths=found_paths,
                    ))

            # The list of requested reports to be generated
            if 'reports' not in conf:
                raise ValueError('Missing reports section in config file: {}'.format(path))
            self.reports = []
            for report in conf['reports']:
                # Known report formats?
                if report['format'] not in Reports:
                    raise ValueError('Unrecognized report file format: {} not in {}'.format(report['format'], Reports))
                # Custom date range specified?
                if 'date_range' in report:
                    date_range = DateRange(
                        start=report['date_range'].get('start'),
                        end=report['date_range'].get('end'),
                        tz=report['date_range'].get('tz'),
                    )
                else:
                    date_range = self.date_range
                # Expand the path and add this to the list of requested reports to generate
                self.reports.append(ConfigData.__ReportConfig(
                    report=Reports[report['format']],
                    output=os.path.expanduser(report['output']),
                    date_range=date_range,
                ))

        def __pretty__(self, p, cycle):
            p.text('<{0}: '.format(type(self).__name__))
            if cycle:
                pass
            else:
                p.pretty({
                    'date_range': p.pretty(self.date_range),
                    'inputs': p.pretty(self.inputs),
                })
            p.text('>')

    # Singleton handler
    instance = None

    def __init__(self):
        if not ConfigData.instance:
            ConfigData.instance = ConfigData.__ConfigData()

    def __getattr__(self, name):
        return getattr(self.instance, name)

# Instantiate our singleton instance
Config = ConfigData()
