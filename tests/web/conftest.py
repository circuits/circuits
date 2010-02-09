def pytest_sessionstart():
    app.start()

def pytest_sessionfinish():
    app.stop()
