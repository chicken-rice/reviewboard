import logging

from django.db.models import Manager

from django.utils import timezone


class AbstractTrophy(object):
    def __init__(self, icon_url, title, descrip):
        self.icon_url = icon_url
        self.title = title
        self.descrip = descrip

    def isQualified(self, user, review_request):
        #Does the user qualify for the Trophy?
        #ToDo implement at inherited class
        return False

class MilestoneTrophy(AbstractTrophy):
    def __init__(self):
        AbstractTrophy.__init__(self,
                                'rb/images/trophy.png',
                                'milestone',
                                 'milestone trophy')

    def isQualified(self, review_request, user):
        rid = review_request.id
        ridstr = str(rid)
        if rid >= 1000:
            trailing = ridstr[1:]
            if trailing == "0" * len(trailing):
                return True
        return False


class PalindromeTrophy(AbstractTrophy):
    def __init__(self):
        AbstractTrophy.__init__(self,
                                'rb/images/fish-trophy.png',
                                'palindrome',
                                 'palindrome trophy')

    def isQualified(self, review_request, user):
        rid = review_request.id
        ridstr = str(rid)
        if rid >= 1000:
            if ridstr == ''.join(reversed(ridstr)):
                return True
        return False


class TrophyManager(Manager):
    """A manager for Trophy models."""
    trophy_kind = [MilestoneTrophy(),
                   PalindromeTrophy()]
    trophy_dict = {}
    for ab_trophy in trophy_kind:
        trophy_dict[ab_trophy.title] = ab_trophy


    def getAbstractTrophy(self, tid):
        trophy = self.objects.get(pk=tid)
        return trophy_dict[trophy.trophy_type]

    def compute_trophies(self, review_request, user):
        """Returns None.

        compute and store the trophy to database.
        """
        from reviewboard.accounts.models import Trophy

        for ab_trophy in self.trophy_kind:
            if ab_trophy.isQualified(review_request, user):
                trophy = Trophy(trophy_type=ab_trophy.title,
                                review_request=review_request, user=user)
                trophy.save()
        return
