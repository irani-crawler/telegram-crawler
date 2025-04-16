def commit_ignore_duplicates(session, obj):
    try:
        session.add(obj)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"[⚠] DB Commit Failed: {e}")
