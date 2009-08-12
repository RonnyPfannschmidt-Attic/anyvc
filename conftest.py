def pytest_collect_directory(path, parent):
    for compiled_module in path.listdir("*.pyc"):
        if not compiled_module.new(ext=".py").check():
            compiled_module.remove()

