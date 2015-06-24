import json
from django.core.management.base import LabelCommand
from django.core.urlresolvers import resolve, Resolver404
import sys


def resolve_url(url):
    if '?' in url:
        url, querystring = url.split('?')
    else:
        querystring = ''
    try:
        match = resolve(url)
    except Resolver404:
        return {"url": url, "querystring": querystring}
    else:
        return {"url": url, "querystring": querystring,
                'view': match.func.__module__ + '.' + match.func.__name__,
                'kwargs': match.kwargs}


class Command(LabelCommand):
    help = "Prints the paths of all the static files"

    def handle(self, *args, **options):
        for line in sys.stdin:
            # Split line and url first
            line = line.strip()
            try:
                url, time = line.split(' ')
            except ValueError:
                raise ValueError('Bad URL (no time included) {}'.format(line))
            out = resolve_url(url)
            out['time'] = time
            print json.dumps(out)
