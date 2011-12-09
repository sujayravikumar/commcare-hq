try:
    from corehq.apps.app_manager.tests.test_app_manager import *
    from corehq.apps.app_manager.tests.test_xml_parsing import *
    from corehq.apps.app_manager.tests.test_xform_parsing import *
    from corehq.apps.app_manager.tests.test_success_message import *
except ImportError, e:
    # for some reason the test harness squashes these so log them here for clarity
    # otherwise debugging is a pain
    import logging
    logging.exception(e)
    raise
