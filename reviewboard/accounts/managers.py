from django.db.models import Manager
from django.utils.translation import ugettext as _


class AbstractTrophy(object):
    def __init__(self, id, icon_url, title, description):
        self.id = id
        self.icon_url = icon_url
        self.title = title
        self.description = description

    def is_qualified(self, user, review_request):
        """
        Determines if the user qualifies for a trophy.

        Returns boolean(True or False) at override method whether
        being qualified from judging of user and review_request.
        """
        return False


class MilestoneTrophy(AbstractTrophy):
    """
    MilestoneTrophy is a kind of neat number trophy.

    This trophy is qualified when the review_request number has
    trailing zeroes.
    ex: id=1000, id=2000, id=10000, id=12000
    """
    def __init__(self):
        description = _('Review request ID has trailing zeroes')
        super(MilestoneTrophy, self).__init__('milestone',
                                              'rb/images/trophy.png',
                                              'Milestone Trophy',
                                              description)

    def is_qualified(self, review_request, user):
        rid = review_request.id
        ridstr = str(rid)
        if rid >= 1000:
            trailing = ridstr[1:]
            if trailing == "0" * len(trailing):
                return True
        return False


class PalindromeTrophy(AbstractTrophy):
    """
    PalindromeTrophy is a kind of neat number trophy.

    This trophy is qualified when the review_request number is
    palindrome
    ex: id=1221, id=1111, id=12321
    """
    def __init__(self):
        description = _('Review request ID is palindrome')
        super(PalindromeTrophy, self).__init__('palindrome',
                                               'rb/images/fish-trophy.png',
                                               'Palindrome Trophy',
                                               description)

    def is_qualified(self, review_request, user):
        rid = review_request.id
        ridstr = str(rid)
        if rid >= 1000:
            if ridstr == ''.join(reversed(ridstr)):
                return True
        return False


class TrophyManager(Manager):
    """
    A manager for Trophy models.

    This manager compute whether trophies should be created and
    connected to review_request.
    This manager only knows trophy types and provide these information.
    """
    def __init__(self):
        super(TrophyManager, self).__init__()
        all_trophies = [MilestoneTrophy(), PalindromeTrophy()]
        self.trophy_dict = {}

        for trophy in all_trophies:
            self.trophy_dict[trophy.id] = trophy

    def get_trophy(self, trophy):
        return self.trophy_dict[trophy.trophy_type]

    def compute_trophies(self, review_request, user):
        """
        Returns None.

        Compute and store the trophies to database.
        """
        from reviewboard.accounts.models import Trophy

        for trophy in self.trophy_dict.values():
            if trophy.is_qualified(review_request, user):
                Trophy(trophy_type=trophy.id,
                       review_request=review_request, user=user)\
                    .save()
        return
