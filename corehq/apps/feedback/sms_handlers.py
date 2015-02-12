import logging
from corehq.apps.feedback.models import FeedbackConfiguration


def send_feedback(reminder, handler, recipient):
    feedback_config = FeedbackConfiguration.by_reminder_id(handler._id)
    if not feedback_config:
        logging.error('reminder handler {} references non-existent feedback config'.format(handler._id))
    return feedback_config.get_message(recipient)
