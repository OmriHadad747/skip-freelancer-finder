import datetime

from datetime import datetime, date


# TODO write docstring for this class
# TODO find better implementation for that


def custom_serializer(obj):
    """
    JSON serializer for objects not serializable by default
    """

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
