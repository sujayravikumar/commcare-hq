GROUP_INDEX = "hqgroups_4o68yn4x87uo2u88e5i27zhl1vhh29uq"
GROUP_MAPPING = {
    "date_formats": [
        "yyyy-MM-dd",
        "yyyy-MM-dd'T'HH:mm:ssZZ",
        "yyyy-MM-dd'T'HH:mm:ss.SSSSSS",
        "yyyy-MM-dd'T'HH:mm:ss.SSSSSS'Z'",
        "yyyy-MM-dd'T'HH:mm:ss'Z'",
        "yyyy-MM-dd'T'HH:mm:ssZ",
        "yyyy-MM-dd'T'HH:mm:ssZZ'Z'",
        "yyyy-MM-dd'T'HH:mm:ss.SSSZZ",
        "yyyy-MM-dd'T'HH:mm:ss",
        "yyyy-MM-dd' 'HH:mm:ss",
        "yyyy-MM-dd' 'HH:mm:ss.SSSSSS",
        "mm/dd/yy' 'HH:mm:ss"
    ],
    "dynamic": False,
    "_meta": {
        "comment": "Modified by Ethan 2014-03-28 for ElasticSearch 1.x syntax",
        "created": None
    },
    "date_detection": False,
    "properties": {
        "doc_type": {
            "index": "not_analyzed",
            "type": "string"
        },
        "domain": {
            "fields": {
                "exact": {
                    "index": "not_analyzed"
                }
            },
            "type": "string"
        },
        "name": {
            "fields": {
                "exact": {
                    "index": "analyzed",
                    "analyzer": "sortable_exact"
                }
            },
            "type": "string"
        },
        "reporting": {"type": "boolean"},
        "path": {"type": "string"},
        "case_sharing": {"type": "boolean"},
        "users": {"type": "string"},
    }
}
