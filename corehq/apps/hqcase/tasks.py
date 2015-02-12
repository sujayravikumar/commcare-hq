import uuid
from celery.task import task
from casexml.apps.phone.xml import get_case_xml
from corehq.apps.hqcase.utils import submit_case_blocks, make_creating_casexml
from corehq.apps.users.models import CommCareUser
from casexml.apps.case import const
from casexml.apps.case.models import CommCareCase
from dimagi.utils.couch.database import iter_docs
from soil import DownloadBase


@task
def explode_case_task(user_id, domain, factor, include_attachments=False):
    return explode_cases(user_id, domain, factor, include_attachments, task=explode_case_task)


def explode_cases(user_id, domain, factor, include_attachments=False, task=None):
    user = CommCareUser.get_by_user_id(user_id, domain)
    keys = [[domain, owner_id, False] for owner_id in user.get_owner_ids()]
    messages = []
    if task:
        DownloadBase.set_progress(task, 0, 0)
    count = 0
    case_ids = [res['id'] for res in CommCareCase.get_db().view(
        'hqcase/by_owner',
        keys=keys,
        include_docs=False,
        reduce=False
    )]
    if include_attachments:
        for case_doc in iter_docs(CommCareCase.get_db(), case_ids):
            case = CommCareCase.wrap(case_doc)
            for i in range(factor - 1):
                new_case_id = uuid.uuid4().hex
                case_block, attachments = make_creating_casexml(case, new_case_id)
                submit_case_blocks(case_block, domain, attachments=attachments)
                if task:
                    DownloadBase.set_progress(explode_case_task, count + 1, 0)
    else:
        # when not using attachments we can use a simpler, optimized version
        # and also preserve parent/child relationships
        processed = {}  # will map old IDs to lists of new IDs
        pending = []

        def can_process(case):
            return not case.indices or all([index.referenced_id in processed for index in case.indices])

        def explode(case):
            # uses closures
            old_case_id = case._id
            old_indices = [index.referenced_id for index in case.indices]
            new_ids = []
            new_case_blocks = []
            for i in range(factor - 1):
                # make a copy
                new_id = uuid.uuid4().hex
                case._id = new_id
                for index_num, index in enumerate(case.indices):
                    index.referenced_id = processed[old_indices[index_num]][i]
                # todo: this doesn't properly handle closed cases
                new_case_blocks.append(get_case_xml(
                    case,
                    (const.CASE_ACTION_CREATE, const.CASE_ACTION_UPDATE),
                    version='2.0'
                ))
                new_ids.append(new_id)

            processed[old_case_id] = new_ids
            submit_case_blocks(new_case_blocks, domain)

        for case_doc in iter_docs(CommCareCase.get_db(), case_ids):
            case = CommCareCase.wrap(case_doc)
            if can_process(case):
                explode(case)
            else:
                pending.append(case)

        max_iterations = len(pending) * len(pending)  # worst case scenario is n^2
        count = 0
        while pending:
            if count > max_iterations:
                raise Exception('cases had inconsistent references to each other.')

            case = pending.pop(0)
            if can_process(case):
                explode(case)
            else:
                pending.append(case)
            count += 1

    messages.append("All of %s's cases were exploded by a factor of %d" % (user.raw_username, factor))

    return {'messages': messages}


def submit_case(case, new_case_id, domain, new_parent_ids=dict()):
    case_block, attachments = make_creating_casexml(case, new_case_id, new_parent_ids)
    submit_case_blocks(case_block, domain, attachments=attachments)
