def get_backend(name: str):
    if name == "matplotlib":
        from .matplotlib import MatplotlibBackend

        return MatplotlibBackend
    else:
        raise ValueError("backend '{}' is not supported".format(name))
