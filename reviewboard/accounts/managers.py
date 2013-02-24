import logging

from django.db.models import Manager

from django.utils import timezone


class TrophyManager(Manager):
    """A manager for Trophy models."""

    def compute_trophies(self, review_request, user):
        """Returns None.

        compute and store the trophy to database.
        """
        from reviewboard.accounts.models import Trophy
        rid = review_request.id
        if rid < 1000:
            return

        ridstr = str(rid)
        interesting = False

        if rid >= 1000:
            trailing = ridstr[1:]
            if trailing == "0" * len(trailing):
                trophy = Trophy(trophy_type='milestone',
                                review_request=review_request, user=user)
                trophy.save()

        if not interesting:
            if ridstr == ''.join(reversed(ridstr)):
                trophy = Trophy(trophy_type='pailindrome',
                                review_request=review_request, user=user)
                trophy.save()
        return
