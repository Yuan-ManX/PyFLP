# type: ignore

from __future__ import annotations

import enum
import inspect
import os
import re
import sys

import m2r2

sys.path.insert(0, os.path.abspath(".."))

from pyflp._descriptors import EventProp, NestedProp, StructProp
from pyflp._events import EventEnum
from pyflp._models import ModelBase

BITLY_LINK = re.compile(r"!\[.*\]\((https://bit\.ly/[A-z0-9]*)\)")
NEW_IN_FL = re.compile(r"\*New in FL Studio v([^\*]*)\*[\.:](.*)")
EVENT_ID_DOC = re.compile(r"([0-9\.]*)\+")
FL_BADGE = "https://img.shields.io/badge/FL%20Studio-{}+-5f686d?labelColor=ff7629&style=for-the-badge"
GHUC_PREFIX = "https://raw.githubusercontent.com/demberto/PyFLP/master/docs/"
IGNORED_BITLY = ["3RDM1yn"]

project = "PyFLP"
copyright = "2022, demberto"
author = "demberto"
release = "2.0.0a1"  # Auto-updated by tbump
extensions = [
    "hoverxref.extension",
    "m2r2",  # Markdown to reStructuredText conversion
    "sphinx_copybutton",  # Copy button for code blocks
    "sphinx_design",  # Grids, cards, icons and tabs
    "sphinx.ext.autodoc",  # Sphinx secret sauce
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",  # Find what I missed to autodoc
    "sphinx.ext.duration",
    "sphinx.ext.intersphinx",  # Automatic links to Python docs
    "sphinx.ext.napoleon",  # Google-style docstrings
    "sphinx.ext.todo",  # Items I need to document
    "sphinx.ext.viewcode",  # "Show source" button next to autodoc output
    "sphinx_toolbox",  # Badges and goodies
    "sphinx_toolbox.github",
    "sphinx_toolbox.more_autodoc.autoprotocol",
    "sphinx_toolbox.more_autodoc.sourcelink",
    "sphinx_toolbox.sidebar_links",
    "sphinx_toolbox.wikipedia",
]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "furo"  # Nice light/dark theme; has an auto-switch mode
autodoc_inherit_docstrings = False
autodoc_default_options = {
    "undoc-members": True,  # Show undocumented members
    "exclude-members": "INTERNAL_NAME",  # Exclude these members
    "no-value": True,  # Don't show a default value (for descriptors mainly)
}
needs_sphinx = "5.0"
hoverxref_auto_ref = True
napoleon_preprocess_types = True
napoleon_attr_annotations = True
html_permalinks_icon = "<span>#</span>"
github_username = author
github_repository = project
autodoc_show_sourcelink = True  # sphinx_toolbox.more_autodoc.sourcelink
todo_include_todos = True  # Include .. todo:: directives in output
todo_emit_warnings = True  # Emit warnings about it as well, so I don't forget
html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css"
]  # https://sphinx-design.readthedocs.io/en/furo-theme/badges_buttons.html#fontawesome-icons
sd_fontawesome_latex = True


def badge_flstudio(app, what, name, obj, options, lines):
    for line in lines:
        if name.split(".")[-2].endswith("ID"):  # Event ID member
            match = EVENT_ID_DOC.fullmatch(line)
        else:
            match = NEW_IN_FL.fullmatch(line)

        if match is not None:
            groups = tuple(
                filter(
                    lambda group: group != "",
                    map(lambda group: group.strip(), match.groups()),
                )
            )

            if len(groups) == 1:
                lines.insert(0, f".. image:: {FL_BADGE.format(groups[0])}")
                lines.insert(1, "")
            elif len(groups) == 2:
                grid = f"""
                .. figure:: {FL_BADGE.format(groups[0])}
                    :alt: New in FL Studio v{groups[0]}

                    {groups[1].strip()}

                """
                lines[:0] = grid.splitlines()  # https://stackoverflow.com/a/25855473
            lines.remove(line)


def add_annotations(app, what, name, obj, options, signature, return_annotation):
    if what == "class" and issubclass(obj, ModelBase):
        annotations = {}
        for name_, type in vars(obj).items():
            if isinstance(obj, NestedProp):
                annotations[name_] = type._type
            elif hasattr(type, "__orig_class__"):
                annotations[name_] = type.__orig_class__.__args__[0]

            if isinstance(type, (EventProp, StructProp)):
                annotations[name_] |= None

        if hasattr(obj, "__annotations__"):
            obj.__annotations__.update(annotations)
        else:
            obj.__annotations__ = annotations


def autodoc_markdown(app, what, name, obj, options, lines):
    filtered = [line for line in lines for link in IGNORED_BITLY if link not in line]
    newlines = m2r2.convert("\n".join(filtered)).splitlines()
    lines.clear()
    lines.extend(newlines)


def remove_model_signature(app, what, name, obj, options, signature, return_annotation):
    """Removes the :func:`ModelBase.__init__` args from the docstrings.

    It's an implementation detail, and only clutters the docs.
    """
    if what == "class" and issubclass(obj, ModelBase):
        return ("", return_annotation)


def remove_enum_signature(app, what, name, obj, options, signature, return_annotation):
    """Removes erroneous :attr:`signature` = '(value)' for `enum.Enum` subclasses."""
    if inspect.isclass(obj) and issubclass(obj, enum.Enum):  # Event ID class
        return ("", return_annotation)


def include_obsolete_ids(app, what, name, obj, skip, options):
    """Includes obsolete / undocumented (prefixed with a `_`) event IDs."""
    if isinstance(obj, EventEnum):  # EventID member
        return False


def show_model_dunders(app, what, name, obj, skip, options):
    """ModelBase subclasses show these dunders regardless of any settings."""
    if name in ("__getitem__", "__setitem__", "__iter__", "__len__", "__index__"):
        return False


def setup(app):
    app.connect("autodoc-process-docstring", badge_flstudio)
    app.connect("autodoc-process-docstring", autodoc_markdown)
    app.connect("autodoc-process-signature", add_annotations)
    app.connect("autodoc-process-signature", remove_model_signature)
    app.connect("autodoc-process-signature", remove_enum_signature)
    app.connect("autodoc-skip-member", include_obsolete_ids)
    app.connect("autodoc-skip-member", show_model_dunders)
