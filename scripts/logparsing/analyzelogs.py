import sys
import json
from collections import defaultdict


if __name__ == '__main__':
    hits_by_view = defaultdict(list)
    none_views = list
    for line in sys.stdin:
        url_info = json.loads(line)
        hits_by_view[url_info.get('view')].append(float(url_info['time']))
        none_views.append(url_info['url']) if url_info.get('view') is None
    # Items in counts are (view, total time, total views)
    counts = sorted([(key, sum(value), len(value)) for key, value in hits_by_view.items()],
                    key=lambda (key, value, _): -value)
    print '%6s %10s %6s %s' % ('Count', 'Time', 'Avg', 'View')
    for view, total_time, count in counts:
        print '%6s %10s %2.3f %s' % (count, total_time, total_time/float(count), view)

    # Figure out which urls aren't getting resolved
    print '\n\n URLS without attached view'
    for url in none_views[:100]:
        print url
