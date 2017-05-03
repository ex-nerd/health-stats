

from .log_parser.csv.mysugr import MySugrLogParser
from .log_parser.csv.onetouchreveal import OneTouchRevealLogParser
from .log_parser.healthkit import HealthkitLogParser
from .log_parser.csv.dexcom_clarity import DexcomClarityLogParser

Parsers = {
    'mysugr_csv': MySugrLogParser,
    'onetouchreveal_csv': OneTouchRevealLogParser,
    'healthkit_zip': HealthkitLogParser,
    'dexcom_clarity_csv': DexcomClarityLogParser,
}
