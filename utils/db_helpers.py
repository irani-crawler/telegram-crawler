def commit_ignore_duplicates(session, obj):
    """
    Commit an object to the session, rolling back on error (e.g. duplicates).
    """
    try:
        session.add(obj)
        session.commit()
    except Exception:
        session.rollback()