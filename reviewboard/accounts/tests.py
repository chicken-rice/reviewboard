import copy

from django.contrib.auth.models import User
from djblets.testing.decorators import add_fixtures
from djblets.testing.testcases import TestCase

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


class TrophyTest(TestCase):
    """Testing the Trophy model."""
    fixtures = ['test_users', 'test_reviewrequests']

    def test_is_trophy_entry_with_milestone(self):
        """Testing entry with milestone."""
        user1 = User.objects.get(pk=1)
        self.assertEqual(len(ReviewRequest.objects.all()), 8)
        review_request1 = copy.deepcopy(ReviewRequest.objects.public()[0])
        review_request1.id = 1000
        review_request1.local_site_id = 1000
        review_request1.local_id = 1000
        review_request1.save()
        self.assertEqual(len(ReviewRequest.objects.all()), 9)
        Trophy.objects.compute_trophies(review_request1, user1)

        trophy_stored = Trophy.objects.get(id=1)
        self.assertEqual(trophy_stored.user, user1)
        self.assertEqual(trophy_stored.review_request, review_request1)
        self.assertNotEqual(trophy_stored.trophy_type, 'pailindrome')
        self.assertEqual(trophy_stored.trophy_type, 'milestone')

    def test_is_trophy_entry_with_pailindrome(self):
        """Testing entry with pailindrome."""
        user1 = User.objects.get(pk=1)
        self.assertEqual(len(ReviewRequest.objects.all()), 8)
        review_request1 = copy.deepcopy(ReviewRequest.objects.public()[0])
        review_request1.id = 1221
        review_request1.local_site_id = 1221
        review_request1.local_id = 1221
        review_request1.save()
        self.assertEqual(len(ReviewRequest.objects.all()), 9)
        Trophy.objects.compute_trophies(review_request1, user1)

        trophy_stored = Trophy.objects.get(id=1)
        self.assertEqual(trophy_stored.user, user1)
        self.assertEqual(trophy_stored.review_request, review_request1)
        self.assertEqual(trophy_stored.trophy_type, 'pailindrome')
        self.assertNotEqual(trophy_stored.trophy_type, 'milestone')

    def test_is_trophy_associated_with_user(self):
        """Testing trophies are associated with user."""
        user1 = User.objects.get(pk=1)
        self.assertEqual(len(ReviewRequest.objects.all()), 8)

        review_request1 = copy.deepcopy(ReviewRequest.objects.public()[0])
        review_request1.id = 1000
        review_request1.local_site_id = 1000
        review_request1.local_id = 1000
        review_request1.save()
        self.assertEqual(len(ReviewRequest.objects.all()), 9)
        Trophy.objects.compute_trophies(review_request1, user1)

        review_request2 = copy.deepcopy(ReviewRequest.objects.public()[0])
        review_request2.id = 1771
        review_request2.local_site_id = 1771
        review_request2.local_id = 1771
        review_request2.save()
        self.assertEqual(len(ReviewRequest.objects.all()), 10)
        Trophy.objects.compute_trophies(review_request2, user1)

        user_trophies = Trophy.objects.filter(user=user1)
        self.assertEqual(len(user_trophies), 2)
        self.assertEqual(user_trophies[0].trophy_type, 'milestone')
        self.assertEqual(user_trophies[1].trophy_type, 'pailindrome')
