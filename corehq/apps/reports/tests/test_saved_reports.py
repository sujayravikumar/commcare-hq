from django.test import TestCase, SimpleTestCase
from corehq.apps.accounting import generator
from corehq.apps.reports.models import ReportConfig, SharingSettings, SharingPermission, SHARING_PERMISSIONS_BY_SLUG
from corehq.apps.users.models import UserRole, Permissions, WebUser, DomainMembership


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

        def create_config(owner, shared_with, exclude=None):
            ReportConfig(
                domain=cls.domain,
                owner_id=owner,
                sharing=SharingSettings(
                    shared_with={target: 'read' for target in shared_with},
                    excluded_users=exclude,
                )
            ).save()

        # owned by user
        create_config(cls.user._id, shared_with=[])

        # shared with user directly
        create_config('user2', shared_with=[cls.user._id])

        # shared with user via role
        create_config('user2', shared_with=[cls.custom_role.get_qualified_id()])

        # shared with user via role but user is excluded
        create_config('user2', shared_with=[cls.custom_role.get_qualified_id()], exclude={cls.user._id})

        # not accessible to user
        create_config('user2', shared_with=['third_user', 'user_role:other_role'])

    def test_by_domain_and_owner(self):
        reports = ReportConfig.by_domain_and_owner(self.domain, self.user)
        self.assertEqual(3, len(reports))

    def test_by_domain_and_owner_reduced(self):
        count = ReportConfig.by_domain_and_owner(self.domain, self.user, reduce=True)
        self.assertEqual(3, count)


class SharingPermissionsTests(SimpleTestCase):
    def setUp(self):
        self.domain = 'test_domain'
        self.config = ReportConfig(domain=self.domain, owner_id='user1')

        self.user = WebUser(username='user1', password='123')
        dm = DomainMembership(domain=self.domain, is_admin=True)
        self.user.domain_memberships.append(dm)
        self.user.domains = [self.domain]
        self.user._id = 'abc'

        self.role = dm.role

        self.permission = SHARING_PERMISSIONS_BY_SLUG['edit']

    def test_compare(self):
        p1 = SHARING_PERMISSIONS_BY_SLUG['read']
        p2 = SHARING_PERMISSIONS_BY_SLUG['manage']
        self.assertNotEqual(p1, p2)
        self.assertGreater(p2, p1)
        self.assertEqual(p2, max([p1, p2]))

    def test_share_with_user(self):
        self.config.share_with(self.user, self.permission)
        self.assertEqual(self.permission.slug, self.config.sharing.shared_with[self.user._id])
        self.assertTrue(self.permission, self.config.get_permission_for_user(self.user))

    def test_share_with_role(self):
        self.config.share_with(self.role, self.permission)
        self.assertEqual(self.permission.slug, self.config.sharing.shared_with[self.role.get_qualified_id()])
        self.assertTrue(self.permission, self.config.get_permission_for_user(self.user))

    def test_unshare_with_role(self):
        self.config.share_with(self.role, self.permission)
        self.assertIn(self.role.get_qualified_id(), self.config.sharing.shared_with)

        self.config.unshare_with(self.role)
        self.assertNotIn(self.role.get_qualified_id(), self.config.sharing.shared_with)

    def test_unshare_with_user(self):
        self.config.share_with(self.user, self.permission)
        self.assertIn(self.user._id, self.config.sharing.shared_with)

        self.config.unshare_with(self.user)
        self.assertNotIn(self.user._id, self.config.sharing.shared_with)

    def test_unshare_user_remove(self):
        self.config.share_with(self.user, self.permission)
        self.assertIn(self.user._id, self.config.sharing.shared_with)

        self.config.unshare_with(self.user)
        self.assertNotIn(self.user._id, self.config.sharing.shared_with)

    def test_unshare_user_exclude(self):
        self.config.share_with(self.role, self.permission)
        self.assertIn(self.role.get_qualified_id(), self.config.sharing.shared_with)
        self.assertNotIn(self.user._id, self.config.sharing.shared_with)

        self.config.unshare_with(self.user)
        self.assertIn(self.user._id, self.config.sharing.excluded_users)
        self.assertIsNone(self.config.get_permission_for_user(self.user))

    def test_reshare_with_excluded_user(self):
        self.config.share_with(self.role, self.permission)
        self.config.unshare_with(self.user)
        self.assertIn(self.user._id, self.config.sharing.excluded_users)

        self.config.share_with(self.user, self.permission)
        self.assertIn(self.user._id, self.config.sharing.shared_with)
        self.assertNotIn(self.user._id, self.config.sharing.excluded_users)

    def test_get_permission(self):
        self.config.share_with(self.role, 'read')
        self.config.share_with(self.user, 'manage')
        self.assertEqual('manage', self.config.get_permission_for_user(self.user).slug)
