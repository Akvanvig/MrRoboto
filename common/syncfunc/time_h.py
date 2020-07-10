"""
Time regular expression taken from https://stackoverflow.com/questions/3096860/convert-time-string-expressed-as-numbermhdsw-to-seconds-in-python
"""

import datetime
import re

#
# PRIVATE INTERFACE
#

_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
_UNITS = {'s':'seconds', 
         'm':'minutes', 
         'h':'hours', 
         'd':'days', 
         'w':'weeks'}
_REGCOMPILED = re.compile(r"(?P<val>\d+)(?P<unit>[smhdw]?)", flags=re.I)

#
#  PUBLIC INTERFACE
#

DEFAULT_TIMEDELTA = datetime.timedelta()

def get_current_date() -> datetime.datetime:
    return datetime.datetime.now()

def date_to_str(time : datetime.datetime) -> str:
    return time.strftime(_DATEFORMAT)

def str_to_date(s : str) -> datetime.datetime:
    return datetime.datetime.strptime(s, _DATEFORMAT)

def args_to_delta(**args) -> datetime.timedelta:
    return datetime.timedelta(**args)

def str_to_delta(s : str) -> datetime.timedelta:
    return datetime.timedelta(**{_UNITS.get(m.group('unit').lower(), 'seconds'): int(m.group('val')) for m in _REGCOMPILED.finditer(s)})