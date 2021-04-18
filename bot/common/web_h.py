from urllib.request import urlopen
from functools import partial

#
# PRIVATE INTERFACE
#

def _blocking_network_io(request):
    with urlopen(request) as response:
        return response.read()

#
# PUBLIC INTERFACE
#

def read_website_content(loop, request):
    return loop.run_in_executor(None, Partial(_blocking_network_io, request))
