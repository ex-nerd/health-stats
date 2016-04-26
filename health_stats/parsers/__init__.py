
from .log_parser.csv.mysugr import MySugrLogParser
from .log_parser.csv.onetouchreveal import OneTouchRevealLogParser

Parsers = {
    'mysugr_csv': MySugrLogParser,
    'onetouchreveal_csv': OneTouchRevealLogParser,
}
