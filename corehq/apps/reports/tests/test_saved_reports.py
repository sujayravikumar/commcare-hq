from django.test import TestCase
from corehq.apps.accounting import generator
from corehq.apps.reports.models import ReportConfig, SharingPermission, SharingSettings
from corehq.apps.users.models import UserRole, Permissions


class SavedReportTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.domain = 'test_domain'
        cls.custom_role = UserRole.get_or_create_with_permissions(
            cls.domain,
            Permissions(),
            "Custom Role"
        )
        cls.custom_role.save()

        cls.user = generator.arbitrary_web_user(save=False)
        cls.user.add_domain_membership(cls.domain)
        cls.user.set_role(cls.domain, cls.custom_role.get_qualified_id())
        cls.user.save()

        def create_config(owner, shared_with):
            ReportConfig(
                domain=cls.domain,
                owner_id=owner,
                sharing=SharingSettings(
                    shared_with=[
                        SharingPermission(target=target, permission='read')
                        for target in shared_with
                    ]
                )
            ).save()

        # owned by user
        create_config(cls.user._id, shared_with=[])

        # shared with user directly
        create_config('user2', shared_with=[cls.user._id])

        # shared with user via role
        create_config('user2', shared_with=[cls.custom_role.get_qualified_id()])

        # not accessible to user
        create_config('user2', shared_with=['third_user', 'user_role:other_role'])

    def test_by_domain_and_owner(self):
        reports = ReportConfig.by_domain_and_owner(self.domain, self.user)
        self.assertEqual(3, len(reports))

    def test_by_domain_and_owner_reduced(self):
        count = ReportConfig.by_domain_and_owner(self.domain, self.user, reduce=True)
        self.assertEqual(3, count)
