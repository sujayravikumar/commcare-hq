from corehq.elastic import get_es
from casexml.apps.case.models import CommCareCase
import time
import uuid
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Tests elastic, by saving to the case index and then reading back from it
    and ensuring that it was saved.
    """
    def handle(self, *args, **options):
        doc_id = args[0]
        _test_elastic(doc_id)

def _test_elastic(doc_id):
    elastic = get_es()
    index = 'hqcases_7a8d2b81335e0a8cef1de718313a23b9'
    # doc_id = 'ffe9ff22bc7a4aea88d7cea6b5b89121'
    doc = CommCareCase.get_db().get(doc_id)
    uid = uuid.uuid4().hex
    doc['_rev'] = uid
    post = elastic.post("{}/case/{}/_update".format(index, doc_id), data={"doc": doc})
    print post
    doc_id_query = {
        "filter": {
            "ids": {"values": [doc_id]}
        },
        "fields": ["_id", "_rev"]
    }
    time.sleep(1)
    res = elastic[index].get('_search', data=doc_id_query)
    revback = res['hits']['hits'][0]['fields']['_rev']
    if revback == uid:
        print 'match!'
    else:
        print 'fail!', revback, uid
