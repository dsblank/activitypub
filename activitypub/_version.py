__version__ = "0.0.1"
VERSION = tuple([(int(v) if v.isdigit() else v)
                 for v in __version__.split(".")])
