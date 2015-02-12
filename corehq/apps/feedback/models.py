from couchdbkit import ResourceNotFound
from couchdbkit.ext.django.schema import DocumentSchema, StringProperty, Document, SchemaListProperty, \
    StringListProperty


class ObjectTypeLookup(DocumentSchema):
    """
    A way to reference looking up objects of a particular type,
    e.g. forms with a certain XMLNS, or cases with a certain case type.

    This lets you theoretically define complex SMS templates off of multiple form/case types,
    though none of that will be supported in the first version of the UI.
    """
    id = StringProperty(required=True)
    object_type = StringProperty(required=True, choices=['form'])  # will eventually support cases too
    object_identifier = StringProperty(required=True)  # will eventually support cases too


class FeedbackConfiguration(Document):
    """
    Configuration structure for what performance feedback should go out.
    """
    reminder_id = StringProperty(required=True)
    object_types = SchemaListProperty(ObjectTypeLookup)
    messages = StringListProperty(required=True)

    @classmethod
    def by_reminder_id(cls, reminder_id):
        # we rely on a hard-coded ID mapping instead of relying on couch views,
        # though since these are in a separate database couch views would probably
        # also be fine.
        try:
            return cls.get('feedback-{}'.format(reminder_id))
        except ResourceNotFound:
            return None

    def get_message(self, recipient_user):
        # todo: this should find the right randomized message to send out
        # fill it in with data, and then return it.
        raise NotImplementedError()
