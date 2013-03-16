from django.contrib.auth.models import User
from djblets.testing.decorators import add_fixtures
from djblets.testing.testcases import TestCase

from reviewboard.diffviewer.models import DiffSetHistory
from reviewboard.accounts.models import LocalSiteProfile, Trophy
from reviewboard.reviews.models import ReviewRequest


class ProfileTests(TestCase):
    """Testing the Profile model."""
    fixtures = ['test_users']

    def test_is_profile_visible_with_public(self):
        """Testing User.is_profile_public with public profiles."""
        user1 = User.objects.get(username='admin')
        user2 = User.objects.get(username='doc')

        self.assertTrue(user1.is_profile_visible(user2))

    def test_is_profile_visible_with_private(self):
        """Testing User.is_profile_public with private profiles."""
        user1 = User.objects.get(username='admin')
        user2 = User.objects.get(username='doc')

        profile = user1.get_profile()
        profile.is_private = True
        profile.save()

        self.assertFalse(user1.is_profile_visible(user2))
        self.assertTrue(user1.is_profile_visible(user1))

        user2.is_staff = True
        self.assertTrue(user1.is_profile_visible(user2))

    @add_fixtures(['test_reviewrequests', 'test_scmtools', 'test_site'])
    def test_is_star_unstar_updating_count_correctly(self):
        """Testing if star, unstar affect review request counts correctly."""
        user1 = User.objects.get(username='admin')
        profile1 = user1.get_profile()
        review_request = ReviewRequest.objects.public()[0]

        site_profile = profile1.site_profiles.get(local_site=None)

        profile1.star_review_request(review_request)
        site_profile = LocalSiteProfile.objects.get(pk=site_profile.pk)

        self.assertTrue(review_request in
                        profile1.starred_review_requests.all())
        self.assertEqual(site_profile.starred_public_request_count, 1)

        profile1.unstar_review_request(review_request)
        site_profile = LocalSiteProfile.objects.get(pk=site_profile.pk)

        self.assertFalse(review_request in
                         profile1.starred_review_requests.all())
        self.assertEqual(site_profile.starred_public_request_count, 0)


class TrophyTests(TestCase):
    """Testing the Trophy model."""
    fixtures = ['test_users', 'test_reviewrequests']

    def test_is_trophy_entry_with_milestone(self):
        """Testing entry with milestone."""
        user1 = User.objects.get(pk=1)
        diff_his1 = DiffSetHistory.objects.get(pk=1)
        review_request1 = ReviewRequest(id=1000, submitter=user1,
                                        diffset_history=diff_his1)
        review_request1.save()
        Trophy.objects.compute_trophies(review_request1, user1)

        trophy_stored = Trophy.objects.get(id=1)
        self.assertEqual(trophy_stored.user, user1)
        self.assertEqual(trophy_stored.review_request, review_request1)
        self.assertEqual(trophy_stored.trophy_type, 'milestone')

    def test_is_trophy_entry_with_palindrome(self):
        """Testing entry with palindrome."""
        user1 = User.objects.get(pk=1)
        diff_his1 = DiffSetHistory.objects.get(pk=1)
        review_request1 = ReviewRequest(id=1221, submitter=user1,
                                        diffset_history=diff_his1)
        review_request1.save()
        Trophy.objects.compute_trophies(review_request1, user1)

        trophy_stored = Trophy.objects.get(id=1)
        self.assertEqual(trophy_stored.user, user1)
        self.assertEqual(trophy_stored.review_request, review_request1)
        self.assertEqual(trophy_stored.trophy_type, 'palindrome')

    def test_is_trophy_associated_with_user(self):
        """Testing trophies are associated with user."""
        user1 = User.objects.get(pk=1)
        diff_his1 = DiffSetHistory.objects.get(pk=1)
        review_request1 = ReviewRequest(id=1000, submitter=user1,
                                        diffset_history=diff_his1)
        review_request2 = ReviewRequest(id=1221, submitter=user1,
                                        diffset_history=diff_his1)

        Trophy.objects.compute_trophies(review_request1, user1)
        Trophy.objects.compute_trophies(review_request2, user1)

        user_trophies = Trophy.objects.filter(user=user1)
        self.assertEqual(len(user_trophies), 2)
        self.assertEqual(user_trophies[0].trophy_type, 'milestone')
        self.assertEqual(user_trophies[1].trophy_type, 'palindrome')
