from corehq.pillows.core import DATE_FORMATS_STRING, DATE_FORMATS_ARR

XFORM_INDEX="xforms_3kmrj98bacd5lw16mv99z336tkdzy761"


XFORM_MAPPING = {
    "date_detection": False,
    "date_formats": DATE_FORMATS_ARR, #for parsing the explicitly defined dates
    'ignore_malformed': True,
    'dynamic': False,
    "_meta": {
        "created": 'Modified by Ethan 2014-03-28 for ElasticSearch 1.x syntax', #record keeping on the index.
    },
    "properties": {
        'doc_type': {'type': 'string'},
        "domain": {
            "type": "string",
            "fields": {
                "exact": {"index": "not_analyzed", "type": "string"}
                #exact is full text string match - hyphens get parsed in standard
                # analyzer
                # in queries you can access by domain.exact
            }
        },
        "xmlns": {
            "type": "string",
            "fields": {
                "exact": {"index": "not_analyzed", "type": "string"}
            }
        },
        '@uiVersion': {"type": "string"},
        '@version': {"type": "string"},
        "path": {"type": "string", "index": "not_analyzed"},
        "submit_ip": {"type": "ip"},
        "app_id": {"type": "string", "index": "not_analyzed"},
        "received_on": {
            "type": "date",
            "format": DATE_FORMATS_STRING
        },
        'initial_processing_complete': {"type": "boolean"},
        'partial_submission': {"type": "boolean"},
        "#export_tag": {"type": "string", "index": "not_analyzed"},
        '_attachments': {
            'dynamic': False,
            'type': 'object'
        },
        '__retrieved_case_ids': {'index': 'not_analyzed', 'type': 'string'},
        '__props_for_querying': {'index': 'not_analyzed', 'type': 'string'},
        'form': {
            'dynamic': False,
            'properties': {
                '@name': {"type": "string", "index": "not_analyzed"},
                "#type": {"type": "string", "index": "not_analyzed"},
                'case': {
                    'dynamic': False,
                    'properties': {
                        'date_modified': {
                            "type": "date",
                            "format": DATE_FORMATS_STRING
                        },
                        '@date_modified': {
                            "type": "date",
                            "format": DATE_FORMATS_STRING
                        },
                        #note, the case_id method here assumes single case properties within a form
                        #in order to support multi case properties, a dynamic template needs to be added along with fundamentally altering case queries

                        "@case_id": {"type": "string", "index": "not_analyzed"},
                        "@user_id": {"type": "string", "index": "not_analyzed"},
                        "@xmlns": {"type": "string", "index": "not_analyzed"},


                        "case_id": {"type": "string", "index": "not_analyzed"},
                        "user_id": {"type": "string", "index": "not_analyzed"},
                        "xmlns": {"type": "string", "index": "not_analyzed"},
                    }
                },
                'meta': {
                    'dynamic': False,
                    'properties': {
                        "timeStart": {
                            "type": "date",
                            "format": DATE_FORMATS_STRING
                        },
                        "timeEnd": {
                            "type": "date",
                            "format": DATE_FORMATS_STRING
                        },
                        "userID": {"type": "string", "index": "not_analyzed"},
                        "deviceID": {"type": "string", "index": "not_analyzed"},
                        "instanceID": {"type": "string", "index": "not_analyzed"},
                        "username": {"type": "string", "index": "not_analyzed"},
                        "appVersion": {"type": "string", "index": "not_analyzed"},
                        "CommCareVersion": {"type": "string", "index": "not_analyzed"},
                    }
                },
            },
        },
    }
}
