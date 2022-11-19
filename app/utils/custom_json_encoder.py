import datetime

from datetime import datetime, date


def custom_serializer(obj):
    """
    JSON serializer for objects not serializable by default
    """

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
