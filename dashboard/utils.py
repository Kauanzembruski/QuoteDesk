from .models import ActivityLog


def log_activity(
    user,
    activity_type,
    title,
    description="",
    object_id=None,
):
    ActivityLog.objects.create(
        user=user,
        type=activity_type,
        title=title,
        description=description,
        object_id=object_id,
    )