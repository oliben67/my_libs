"""Module containing decorators used throughout Cembalo."""


def valid_args_names(*valid_names, strict=False, single_arg=False):
    """
    Checks if the correct named arguments are passed to the method

    :param valid_names: list of valid argument names (duplicates automatically removed)
    :type valid_names: ``list[str]``
    :param strict: strict adherence to name arguments list otherwise checks only for intersection
    :type strict: ``bool``
    :param single_arg: one and only named argument can be passed
    :type strict: ``bool``
    :raises ValueError: raises value error when validation of arguments' names fails
    """
    valid_args = set(valid_names)
    valid_list_msg = ", ".join((f"'{a}'" for a in valid_args))
    strictly = "-strickly- " if strict else ""

    def inner_func(func):
        def wrapper(*args, **kwargs):
            args_names = set(kwargs.keys())
            if strict or not args_names.issubset(valid_args):
                args_msg = ", ".join((f"'{a}'" for a in args_names))
                print(not args_names.issubset(valid_args))
                if strict or (args_names.difference(valid_args) == args_names):
                    end_message = (
                        "only"
                        if strict and args_names.issubset(valid_args)
                        else "instead"
                    )
                    raise ValueError(
                        f"Invalid argument names: was {strictly}expecting [{valid_list_msg}], "
                        + f"got [{args_msg}] {end_message}."
                    )
            if single_arg:
                if len(args_names) > 1:
                    raise ValueError(
                        f"Invalid argument names: was {strictly}expecting a single argument "
                        + f"{valid_list_msg}, got {args_msg}] instead."
                    )
            return func(*args, **kwargs)

        return wrapper

    return inner_func


def tracer(filename, dot_output=False, **kwargs):  # dot_theme="color"):
    """ """

    def call_stats(func):
        assert callable(func), "Decorated object needs to a be a callable"

        import cProfile
        import io
        import os
        import pstats
        import time
        from pathlib import Path

        import gprof2dot as todot

        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile(
                builtins=False,
            )
            profiler.enable()
            time_start = time.strftime("%Y%m%d-%H%M%S")
            try:
                return func(*args, **kwargs)
            finally:
                try:
                    time_end = time.strftime("%Y%m%d-%H%M%S")
                    timestamps = f"{time_start}-to-{time_end}"
                    output_filename = (
                        Path(os.path.dirname(filename))
                        / f"{os.path.basename(filename)}.{timestamps}.stats"
                    )
                    profiler.disable()
                    stats_stream = io.StringIO()
                    ps = pstats.Stats(profiler, stream=stats_stream)  # .sort_stats(
                    # "cumtime"
                    # )
                    if dot_output:
                        try:
                            dot_filename = f"{os.path.splitext(output_filename)[0]}.dot"
                            with open(dot_filename, "wt", encoding="UTF-8") as output:
                                # totalMethod = kwargs.get("dot_total_method", "callratios")
                                theme = todot.themes[kwargs.get("dot_theme", "color")]
                                todot.strip = kwargs.get("dot_strip", False)
                                todot.wrap = kwargs.get("dot_strip", False)
                                label_names = (
                                    kwargs.get("dot_node_labels")
                                    or todot.defaultLabelNames
                                )

                                parser = todot.PstatsParser(ps)
                                profile = parser.parse()
                                dot = todot.DotWriter(output)
                                dot.show_function_events = [
                                    todot.labels[name] for name in label_names
                                ]

                                dot.graph(profile, theme)
                        except Exception as ex:  # noqa: B901, E722
                            print(ex)
                    ps.print_stats()
                    with open(output_filename, "w+") as f:
                        f.write(stats_stream.getvalue())
                except Exception as ex:  # noqa: B901, E722
                    print(ex)

        return wrapper

    return call_stats


class ClassPropertyDescriptor:
    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def classproperty(func):
    """ """
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


def delayed(delay: int = 0):
    """
    Delays the execution of the decorated function by the specified amount of time.

    :param delay: the amount of time to delay the execution of the decorated function
    :type delay: ``int``
    """

    def inner_func(func):
        from threading import Timer

        def wrapper(*args, **kwargs):
            if delay == 0:
                return func(*args, **kwargs)
            return Timer(delay, func, args, kwargs).start()

        return wrapper

    return inner_func
