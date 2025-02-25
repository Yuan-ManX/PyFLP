# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

"""Contains the exceptions used by and shared across PyFLP."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._events import EventEnum

__all__ = [
    "Error",
    "NoModelsFound",
    "EventIDOutOfRange",
    "InvalidEventChunkSize",
    "UnexpectedType",
    "PropertyCannotBeSet",
    "HeaderCorrupted",
    "VersionNotDetected",
    "ExpectedValue",
    "ModelNotFound",
]


class Error(Exception):
    """Base class for PyFLP exceptions.

    Some exceptions derive from standard Python exceptions to ease handling.
    """


class EventIDOutOfRange(Error, ValueError):
    def __init__(self, id: int, min_i: int, max_e: int):
        super().__init__(f"Expected ID in {min_i}-{max_e - 1}; got {id} instead")


class InvalidEventChunkSize(Error, TypeError):
    """A fixed size event is created with a wrong amount of bytes."""

    def __init__(self, expected: int, got: int):
        super().__init__(f"Expected a bytes object of length {expected}; got {got}")


class UnexpectedType(Error, TypeError):
    def __init__(self, expected: type, got: type):
        super().__init__(f"Expected a {expected} object; got a {got} object instead")


class PropertyCannotBeSet(Error, AttributeError):
    def __init__(self, *ids: EventEnum):
        super().__init__(f"Event(s) {ids!r} was / were not found")


class ExpectedValue(Error, ValueError):
    def __init__(self, invalid: object, *valid: object):
        super().__init__(f"Invalid value {invalid!r}; expected one of {valid!r}")


class DataCorrupted(Error):
    """Base class for parsing exceptions."""


class HeaderCorrupted(DataCorrupted, ValueError):
    """Header chunk contains an unexpected / invalid value.

    Args:
        desc (str): A string containing details about what is corrupted.
    """

    def __init__(self, desc: str):
        super().__init__(f"Error parsing header: {desc}")


class NoModelsFound(DataCorrupted):
    """Model's `__iter__` method fails to generate any model."""


class ModelNotFound(DataCorrupted, IndexError):
    """An invalid index is passed to model's `__getitem__` method."""


class VersionNotDetected(DataCorrupted):
    """String decoder couldn't be decided due to absence of project version."""
