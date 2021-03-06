# most of it taken from https://github.com/dusty-phillips/opterator
import inspect
from argparse import ArgumentParser
from enum import Enum
from typing import Any, Iterable, Optional, Set

from docstring_parser import parse


def parse_docstring(doc: Optional[str]):
    if doc:
        parsed = parse(doc)
        params = {arg.arg_name: arg.description for arg in parsed.params}
        params = {k: val.replace("\n", " ") for k, val in params.items()}
        return (
            "\n".join(
                (
                    desc
                    for desc in (parsed.short_description, parsed.long_description)
                    if desc
                )
            ),
            params,
        )
    return "", {}


def generate_options():
    """Helper coroutine to identify short options that haven't been used yet.

    Yields lists of short option (if available) and long option for
    the given name, keeping track of which short options have been previously
    used.
    If you aren't familiar with coroutines, use similar to a generator:
    x = generate_options()
    next(x)  # advance coroutine past its initialization code
    params = x.send(param_name)
    """
    used_short_options: Set[str] = set()
    param_name = yield
    while True:
        names = ["--" + param_name]
        for letter in param_name:
            if letter not in used_short_options:
                used_short_options.add(letter)
                names.insert(0, "-" + letter)
                break
        param_name = yield names


def portable_argspec(func):
    """Return function signature.

    given a function, return a tuple of
    (positional_params, keyword_params, varargs, defaults, annotations)
    where
    * positional_params is a list of parameters that don't have default values
    * keyword_params is a list of parameters that have default values
    * varargs is the string name for variable arguments
    * defaults is a dict of default values for the keyword parameters
    * annotations is a dictionary of param_name: annotation pairs
        it may be empty, and on python 2 will always be empty.
    This function is portable between Python 2 and Python 3, and does some
    extra processing of the output from inspect.
    """
    (argnames, _, _, defaults, _, _, annotations,) = inspect.getfullargspec(func)

    kw_params = {}
    if defaults:
        kw_boundary = len(argnames) - len(defaults)
        kw_params = {
            argnames[kw_boundary + idx]: val for idx, val in enumerate(defaults)
        }
        argnames = argnames[:kw_boundary]

    return (
        argnames,
        kw_params,
        annotations,
    )


def get_action(
    _type, default=None,
):
    if default is False:
        return "store_true"
    if default is True:
        return "store_false"
    if issubclass(_type, Iterable):
        return "append"
    return "store"


UNDEFINED = object()
"""sometimes the value could be None. we need this to distinguish such values."""


def get_arg_names(
    param, param_doc, option_generator,
):
    names = []

    while param_doc and param_doc[0].startswith("-"):
        names.append(param_doc.pop(0))

    return names if names else option_generator.send(param)


def add_param(
    parser,
    param: str,
    param_docs: dict,
    _type: Any = UNDEFINED,
    default: Any = UNDEFINED,
    option_generator=None,
):
    param_doc = (param_docs.get(param) or "").split()
    option_kwargs = {}

    names = [param]
    if default is not UNDEFINED:
        option_kwargs["default"] = default
        option_kwargs["dest"] = param
        names = get_arg_names(param, param_doc, option_generator)

    if _type is UNDEFINED:
        _type = type(default)

    option_kwargs.update(
        {"action": get_action(_type, default), "help": " ".join(param_doc),}
    )

    if issubclass(_type, Enum):
        option_kwargs["choices"] = [e.value for e in _type]

    return parser.add_argument(*names, **option_kwargs)


def prepare_arguments(
    parser: ArgumentParser, positional_params, kw_params, annotations: dict, param_docs,
):
    option_generator = generate_options()
    next(option_generator)

    for param in positional_params:
        add_param(parser, param, param_docs, _type=annotations.get(param, UNDEFINED))

    for param, default in kw_params.items():
        add_param(
            parser,
            param,
            param_docs,
            _type=annotations.get(param, UNDEFINED),
            default=default,
            option_generator=option_generator,
        )
    return parser


def opterate(subparser, func):
    """A decorator for a main function entry point to a script.

    It automatically generates the options for the main entry point based on the
    arguments, keyword arguments, and docstring.

    Positional arguments are mandatory arguments that store a string value.
    All keyword arguments in the function definition are options.

    arbitrary args and values can be captured with **kwargs

    Annotations:
        - used to determine the type and action of the arguments
        - list, tuple, Enum are supported, List[Enum] are supported

    The default value assigned to a keyword argument helps determine
        the type of option and action.
    The default value is assigned directly to the parser's default for that option.
    In addition, it determines the ArgumentParser action
        --
        a default value of False implies store_true, while True implies store_false.
        If the default value is a list, the action is append
            (multiple instances of that option are permitted).
        Strings or None imply a store action.


        the format is:
        :param name: [short option and/or long option] help text

        The top part of the docstring becomes the usage message for the app.

        Below that, ReST-style :param: lines in the following format describe the option

    Options are further defined in the docstring.
        :param variable_name: -v --verbose the help_text for the variable
        :param variable_name: -v the help_text no long option
        :param variable_name: --verbose the help_text no short option


        Variable_name is the name of the variable in the function specification and
    must refer to a keyword argument. All options must have a :param: line like
    this.

    If you can have an arbitrary length of positional arguments, add a
    *arglist variable; It can be named with any valid python identifier.
    See tests/* for some examples.

    """

    (positional_params, kw_params, annotations) = portable_argspec(func)
    description, param_docs = parse_docstring(func.__doc__)

    parser = subparser.add_parser(func.__name__, help=description)

    return prepare_arguments(
        parser, positional_params, kw_params, annotations, param_docs
    )


# def wrapper(argv=None):
#     args = vars(parser.parse_args(argv))
#     processed_args = [args[p] for p in positional_params + kw_params]
#     func(*processed_args)
#
#     return wrapper
