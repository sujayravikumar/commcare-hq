import sys
import json
from collections import defaultdict


if __name__ == '__main__':
    hits_by_view = defaultdict(list)
    for line in sys.stdin:
        url_info = json.loads(line)
        hits_by_view[url_info.get('view')].append(float(url_info['time']))
    # Items in counts are (view, total time, total views)
    counts = sorted([(key, sum(value), len(value)) for key, value in hits_by_view.items()],
                    key=lambda (key, value, _): -value)
    for view, total_time, count in counts:
        print '%6s %10s %s' % ('Count', 'Time', 'View')
        print '%6s %10s %s' % (count, total_time, view)
