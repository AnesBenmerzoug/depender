def get_backend(name: str):
    if name == "matplotlib":
        from .matplotlib import MatplotlibBackend

        return MatplotlibBackend
    elif name == "graphviz":
        from .graphviz import GraphivizBackend

        return GraphivizBackend
    else:
        raise ValueError("backend '{}' is not supported".format(name))
