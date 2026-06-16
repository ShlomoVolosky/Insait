def pytest_sessionfinish(session, exitstatus):
    # An empty test suite (pytest's exit code 5, "no tests collected") is not a
    # failure for the scaffold. Becomes a no-op once real tests exist.
    if exitstatus == 5:
        session.exitstatus = 0
