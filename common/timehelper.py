"""
Time regular expression taken from https://stackoverflow.com/questions/3096860/convert-time-string-expressed-as-numbermhdsw-to-seconds-in-python
"""

import datetime
import re

# PRIVATE

_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
_UNITS = {'s':'seconds', 
         'm':'minutes', 
         'h':'hours', 
         'd':'days', 
         'w':'weeks'}

# PUBLIC

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
    return datetime.timedelta(**{_UNITS.get(m.group('unit').lower(), 'seconds'): int(m.group('val')) for m in re.finditer(r'(?P<val>\d+)(?P<unit>[smhdw]?)', s, flags=re.I)})