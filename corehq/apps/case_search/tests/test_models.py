from __future__ import absolute_import

import json
import os

from django.test import TestCase
from mock import call, patch

from corehq.apps.case_search.models import (
    disable_case_search,
    enable_case_search,
    SearchResult,
)


class TestCaseSearch(TestCase):
    domain = "meereen"

    @patch('corehq.apps.case_search.tasks.CaseSearchReindexerFactory')
    def test_enable_case_search_reindex(self, fake_factory):
        """
        When case search is enabled, reindex that domains cases
        """
        enable_case_search(self.domain)
        self.assertEqual(fake_factory.call_args, call(domain=self.domain))
        self.assertTrue(fake_factory().build.called)
        self.assertTrue(fake_factory().build().reindex.called)

    @patch('corehq.apps.case_search.tasks.delete_case_search_cases')
    def test_disable_case_search_reindex(self, fake_deleter):
        """
        When case search is disabled, delete that domains cases
        """
        with patch('corehq.apps.case_search.tasks.CaseSearchReindexerFactory'):
            enable_case_search(self.domain)

        disable_case_search(self.domain)
        self.assertEqual(fake_deleter.call_args, call(self.domain))


class TestSearchResults(TestCase):
    def test_store_search_result(self):
        domain = 'domain'
        user_id = 'userid'
        enable_case_search(domain)
        criteria = {'domain': 'domain', 'property': 'thing', 'other_property': 'other_thing'}

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'fake_hits.json')) as f:
            fake_hits = json.load(f)
            fake_hit_ids = [r['_id'] for r in fake_hits]

        result_object = SearchResult.create(domain, user_id, criteria, fake_hits)
        self.assertEqual(result_object.searched_properties, criteria)
        self.assertEqual(result_object.results, fake_hit_ids)

        self.assertEqual(1, len(SearchResult.objects.all()))
