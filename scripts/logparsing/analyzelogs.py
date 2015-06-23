import sys
import json
from collections import defaultdict


if __name__ == '__main__':
    hits_by_view = defaultdict(list)
    for line in sys.stdin:
        url_info = json.loads(line)
        hits_by_view[url_info.get('view')].append(url_info)
    counts = sorted([(key, len(value)) for key, value in hits_by_view.items()],
                    key=lambda (key, value): -value)
    for view, count in counts:
        print '%6s %s' % (count, view)
