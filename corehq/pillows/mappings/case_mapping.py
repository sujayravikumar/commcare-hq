from corehq.pillows.core import DATE_FORMATS_ARR, DATE_FORMATS_STRING
CASE_INDEX="hqcases_nv2gj2451892i000pvrr68o2x53365oi"

CASE_MAPPING = {
        'date_detection': False,
        'date_formats': DATE_FORMATS_ARR,
        'dynamic': False,
        '_meta': {
            'comment': '',
            'created': 'Modified by Ethan 2014-03-28 for ElasticSearch 1.x syntax'
            },
        'properties': {
            'actions': {
                'dynamic': False,
                'properties': {'action_type': {'type': 'string'},
                'date': {
                    'format': DATE_FORMATS_STRING,
                    'type': 'date'},
                'doc_type': {'index': 'not_analyzed',
                    'type': 'string'},
                'indices': {'dynamic': False,
                    'properties': {'doc_type': {
                        'index': 'not_analyzed',
                        'type': 'string'},
                        'identifier': {
                            'type': 'string'},
                        'referenced_id': {
                            'type': 'string'},
                        'referenced_type': {
                            'type': 'string'}},
                        'type': 'object'},
                'server_date': {
                    'format': DATE_FORMATS_STRING,
                    'type': 'date'},
                'sync_log_id': {'type': 'string'},
                'user_id': {'type': 'string'},
                'xform_id': {'type': 'string'},
                'xform_name': {'type': 'string'},
                'xform_xmlns': {'type': 'string'}},
            'type': 'nested'},
            'closed': {'type': 'boolean'},
            'closed_by': {'type': 'string'},
            'closed_on': {
                'format': DATE_FORMATS_STRING,
                'type': 'date'},
            'computed_': {'enabled': False, 'type': 'object'},
            'computed_modified_on_': {
                'format': DATE_FORMATS_STRING,
                'type': 'date'},
            'doc_type': {'index': 'not_analyzed', 'type': 'string'},
            'domain': {'fields': {'exact': {'index': 'not_analyzed'}},
                'type': 'string'},
            'export_tag': {'type': 'string'},
            'external_id': {'fields': {'exact': {'index': 'not_analyzed'}},
                'type': 'string'},
            'indices': {'dynamic': False,
                'properties': {'doc_type': {'index': 'not_analyzed',
                    'type': 'string'},
                    'identifier': {'type': 'string'},
                    'referenced_id': {'type': 'string'},
                    'referenced_type': {'type': 'string'}},
                'type': 'object'},
            'initial_processing_complete': {'type': 'boolean'},
                               'location_': {'type': 'string'},
                               'modified_on': {
                                       'format': DATE_FORMATS_STRING,
                                       'type': 'date'},
                               'name': {'fields': {'exact': {'index': 'not_analyzed'}},
                                   'type': 'string'},
                               'opened_by': {'type': 'string'},
                               'opened_on': {
                                       'format': DATE_FORMATS_STRING,
                                       'type': 'date'},
                               'owner_id': {'type': 'string'},
                               'referrals': {'enabled': False, 'type': 'object'},
                               'server_modified_on': {
                                       'format': DATE_FORMATS_STRING,
                                       'type': 'date'},
                               'type': {'fields': {'exact': {'index': 'not_analyzed'}},
                                   'type': 'string'},
                               'user_id': {'type': 'string'},
                               'version': {'type': 'string'},
                               'xform_ids': {'index': 'not_analyzed', 'type': 'string'},
                               'contact_phone_number': {'index': 'not_analyzed', 'type': 'string'},
                               }
               }
