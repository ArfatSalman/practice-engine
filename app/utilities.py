from __future__ import print_function
import sys

def print_debug(*args, **kwargs):
	return print(*args, file=sys.stderr, **kwargs)