from django.core.urlresolvers import resolve
import sys


def resolve_url(url):
    match = resolve(url)
    return match.func.__module__ + '.' + match.func.__name__, match.kwargs


if __name__ == '__main__':
    for line in sys.stdin:
        print resolve_url(line)
