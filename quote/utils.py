from accounts.models import User
from .models import Quote


def quotes_for_user(user):

    if user.role == User.Role.ADMIN:
        return Quote.objects.all()

    if user.role == User.Role.SELLER:
        return Quote.objects.filter(
            created_by=user
        )

    return Quote.objects.none()