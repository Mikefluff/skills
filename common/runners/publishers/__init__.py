"""Social-platform publishing layer.

Each module registers one Publisher via config.register_publisher(). Import
them through config.load_all_publishers() rather than directly, so a broken
vendor module cannot crash `--list-platforms`.
"""
