import sys
import json
from collections import defaultdict
from decimal import *


if __name__ == '__main__':
    hits_by_view = defaultdict(list)
    for line in sys.stdin:
        url_info = json.loads(line)
        hits_by_view[url_info.get('view')].append(float(url_info['time']))
    # Items in counts are (view, total time, total views)
    counts = sorted([(key, sum(value), len(value)) for key, value in hits_by_view.items()],
                    key=lambda (key, value, _): -value)
    print '%6s %10s %10s %s' % ('Count', 'Time', 'Avg', 'View')
    for view, total_time, count in counts:
        getcontext().prec = 7
        print '%6s %10s %10s %s' % (count, total_time, Decimal(total_time/float(count)), view)
