from datetime import UTC, datetime


def utcnow():
    """Return a naive UTC datetime without using deprecated utcnow()."""
    return datetime.now(UTC).replace(tzinfo=None)


def utcfromtimestamp(timestamp):
    """Return a naive UTC datetime from a Unix timestamp."""
    return datetime.fromtimestamp(timestamp, UTC).replace(tzinfo=None)