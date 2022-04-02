import abc
import enum
from typing import TypeVar, Union

import colour
from bytesioex import Byte, Int, SByte, UInt

from pyflp.constants import BYTE, DATA, DATA_TEXT_EVENTS, DWORD, TEXT, WORD
from pyflp.utils import buflen_to_varint


class _Event(abc.ABC):
    """Abstract base class representing an event."""

    _count = 0

    @abc.abstractproperty
    def size(self) -> int:
        """Raw event size in bytes."""

    @property
    def index(self) -> int:
        return self.__index

    @abc.abstractmethod
    def dump(self, new_data):
        """Converts Python data types into bytes
        objects and dumps them to `self.data`."""

    def to_raw(self) -> bytes:
        """Used by Project.save(). Overriden by `_VariabledSizedEvent`."""
        return int.to_bytes(self.id, 1, "little") + self.data

    def __repr__(self) -> str:
        cls = type(self).__name__
        sid = str(self.id)
        iid = int(self.id)
        if isinstance(self.id, enum.IntEnum):
            return f"{cls!r} id={sid!r}, {iid!r}"
        return f"{cls!r} id={iid!r}"

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, type(self)):
            raise TypeError(
                f"Cannot compare equality between an 'Event' and {type(o)!r}"
            )
        return self.id == o.id and self.data == o.data

    def __ne__(self, o: object) -> bool:
        if not isinstance(o, type(self)):
            raise TypeError(
                f"Cannot compare inequality between an 'Event' and {type(o)!r}"
            )
        return self.id != o.id or self.data != o.data

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID from **0** to **255**.
            data (bytes): A `bytes` object.
        """

        self.id = id
        self.data = data
        self.__index = _Event._count
        _Event._count += 1
        super().__init__()


_EventType = TypeVar("_EventType", bound=_Event)


class _VariableSizedEvent(_Event):
    """Implements `Event.size` and `Event.to_raw` for `TextEvent` and `DataEvent`."""

    @property
    def size(self) -> int:
        if self.data:
            return 1 + len(buflen_to_varint(self.data)) + len(self.data)
        return 2

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        iid = int(self.id)
        if isinstance(self.id, enum.IntEnum):
            return f"<{cls!r} id={self.id.name!r} ({iid!r}), size={self.size!r}>"
        return f"<{cls!r} id={iid!r}, size={self.size!r}>"

    def to_raw(self) -> bytes:
        id = int.to_bytes(self.id, 1, "little")
        length = buflen_to_varint(self.data) if self.data else b"\x00"
        data = self.data
        return id + length + data if self.data else id + length


class _ByteEvent(_Event):
    """Represents a byte-sized event."""

    @property
    def size(self) -> int:
        return 2

    def dump(self, new_data: Union[bytes, int, bool]):
        """Dumps a single byte of data; either a bool, int or a bytes object to event data.

        Args:
            new_data (Union[bytes, int, bool]): The data to be dumped into the event.

        Raises:
            ValueError: If `new_data` is a bytes object and its size isn't equal to 1.
            OverflowError: When an integer is too big to be accumulated in 1 byte.
            TypeError: When `new_data` isn't a bool, int or a bytes object.
        """

        if isinstance(new_data, bool):
            data = 1 if new_data else 0
            self.data = data.to_bytes(1, "little")
        elif isinstance(new_data, bytes):
            if len(new_data) != 1:
                raise ValueError(
                    f"Expected a bytes object of 1 byte length; got {new_data!r}"
                )
            self.data = new_data
        elif isinstance(new_data, int):
            if new_data != abs(new_data) and new_data not in range(-128, 128):
                raise OverflowError(
                    f"Expected a value of -128 to 127; got {new_data!r}"
                )
            elif new_data > 255:
                raise OverflowError(f"Expected a value from 0 to 255; got {new_data!r}")
            self.data = new_data.to_bytes(1, "little")
        else:
            raise TypeError(
                f"Expected a bytes, bool or an int object; got {type(new_data)!r}"
            )

    def to_uint8(self) -> int:
        return Byte.unpack(self.data)[0]

    def to_int8(self) -> int:
        return SByte.unpack(self.data)[0]

    def to_bool(self) -> bool:
        return self.to_int8() != 0

    def __repr__(self) -> str:
        b = self.to_int8()
        B = self.to_uint8()
        if b == B:
            msg = f"B={B!r}"
        else:
            msg = f"b={b!r}, B={B!r}"
        return f"<{super().__repr__()!r}, {msg!r}>"

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID from **0** to **63**.
            data (bytes): A 1 byte sized `bytes` object.

        Raises:
            ValueError: When `id` is not in range of 0-63.
            TypeError: When size of `data` is not 1.
        """

        if not (id < WORD and id >= BYTE):
            raise ValueError(f"Exepcted 0-63; got {id!r}")
        dl = len(data)
        if dl != 1:
            raise TypeError(f"Unexpected data size; expected 1, got {dl!r}")
        super().__init__(id, data)


class _WordEvent(_Event):
    """Represents a 2 byte event."""

    @property
    def size(self) -> int:
        return 3

    def dump(self, new_data: Union[bytes, int]):
        """Dumps 2 bytes of data; either an int or a bytes object to event data.

        Args:
            new_data (Union[bytes, int]): The data to be dumped into the event.

        Raises:
            ValueError: If `new_data` is a bytes object and its size isn't 2.
            OverflowError: When `new_data` cannot be accumulated in 2 bytes.
            TypeError: When `new_data` isn't an int or a bytes object.
        """

        word = new_data
        if isinstance(word, bytes):
            if len(word) != 2:
                raise ValueError(
                    f"Expected a bytes object of 2 bytes length; got {word!r}"
                )
            self.data = word
        elif isinstance(word, int):
            if word != abs(word) and word not in range(-32768, 32768):
                raise OverflowError(f"Expected a value -32768 to 32767; got {word!r}")
            elif word > 65535:
                raise OverflowError(f"Expected a value of 0 to 65535; got {word!r}")
            self.data = word.to_bytes(2, "little")
        else:
            raise TypeError(f"Expected a bytes or an int object; got {type(word)!r}")

    def to_uint16(self) -> int:
        return int.from_bytes(self.data, "little")

    def to_int16(self) -> int:
        return int.from_bytes(self.data, "little", signed=True)

    def __repr__(self) -> str:
        h = self.to_int16()
        H = self.to_uint16()
        if h == H:
            msg = f"H={H!r}"
        else:
            msg = f"h={h!r}, H={H!r}"
        return f"<{super().__repr__()!r}, {msg!r}>"

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID from **64** to **127**.
            data (bytes): A `bytes` object of size 2.

        Raises:
            ValueError: When `id` is not in range of 64-127.
            TypeError: When size of `data` is not 2.
        """

        if id not in range(WORD, DWORD):
            raise ValueError(f"Exepcted 64-127; got {id!r}")
        if len(data) != 2:
            raise TypeError(
                f"Expected a data of 2 bytes; got a data of size {len(data)!r} instead"
            )
        super().__init__(id, data)


class _DWordEvent(_Event):
    """Represents a 4 byte event."""

    DWORD_MAX = 4_294_967_295
    INT_MIN = -2_147_483_648
    INT_MAX = 2_147_483_647

    @property
    def size(self) -> int:
        return 5

    def dump(self, new_data: Union[bytes, int]):
        """Dumps 4 bytes of data; either an int or a bytes object to event data.

        Args:
            new_data (Union[bytes, int]): The data to be dumped into the event.

        Raises:
            ValueError: If `new_data` is a bytes object and its size isn't 4.
            OverflowError: When an integer is too big to be accumulated in 4 bytes.
            TypeError: When `new_data` isn't an int or a bytes object.
        """

        dword = new_data
        if isinstance(dword, bytes):
            if len(dword) != 4:
                raise ValueError(
                    f"Expected a bytes object of 4 bytes length; got {dword!r}"
                )
            self.data = dword
        elif isinstance(dword, int):
            if dword != abs(dword) and dword not in range(
                self.INT_MIN, self.INT_MAX + 1
            ):
                raise OverflowError(
                    f"Expected a value of {self.INT_MIN!r} "
                    f"to {self.INT_MAX!r}; got {dword!r}"
                )
            elif dword > self.DWORD_MAX:
                raise OverflowError(
                    f"Expected a value of 0 to {self.DWORD_MAX!r}; got {dword!r}"
                )
            self.data = dword.to_bytes(4, "little")
        else:
            raise TypeError(f"Expected a bytes or an int object; got {type(dword)!r}")

    def to_uint32(self) -> int:
        """Deserializes `self.data` as a 32-bit unsigned integer as an `int`."""
        return UInt.unpack(self.data)[0]

    def to_int32(self) -> int:
        """Deserializes `self.data` as a 32-bit signed integer as an `int`."""
        return Int.unpack(self.data)[0]

    def __repr__(self) -> str:
        i32 = self.to_int32()
        u32 = self.to_uint32()
        if i32 == u32:
            msg = f"I={u32!r}"
        else:
            msg = f"i={i32!r}, I={u32!r}"
        return f"<{super().__repr__()!r}, {msg!r}>"

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID from **128** to **191**.
            data (bytes): A `bytes` object of size 4.

        Raises:
            ValueError: When `id` is not in range of 128-191.
            TypeError: When size of `data` is not 4.
        """

        if id not in range(DWORD, TEXT):
            raise ValueError(f"Exepcted 128-191; got {id!r}")
        dl = len(data)
        if dl != 4:
            raise TypeError(f"Unexpected data size; expected 4, got {dl!r}")
        super().__init__(id, data)


_DWordEventType = TypeVar("_DWordEventType", bound=_DWordEvent)


class _ColorEvent(_DWordEvent):
    """Represents a 4 byte event which stores a color."""

    def dump(self, new_color: colour.Color):
        """Dumps a `colour.Color` to event data.

        Args:
            new_color (colour.Color): The color to be dumped into the event.

        Raises:
            TypeError: When `new_color` isn't a `colour.Color` object."""

        if not isinstance(new_color, colour.Color):
            raise TypeError(f"Expected a colour.Color; got {type(new_color)!r}")
        self.data = bytes((int(c * 255) for c in new_color.rgb)) + b"\x00"

    def to_color(self) -> colour.Color:
        r, g, b = (c / 255 for c in self.data[:3])
        return colour.Color(rgb=(r, g, b))


class _TextEvent(_VariableSizedEvent):
    """Represents a variable sized event used for storing strings."""

    uses_unicode = True  # Parser can change this

    @staticmethod
    def as_ascii(buf: bytes):
        return buf.decode("ascii", errors="ignore").strip("\0")

    @staticmethod
    def as_uf16(buf: bytes):
        return buf.decode("utf-16", errors="ignore").strip("\0")

    def dump(self, new_data: str):
        """Dumps a string to the event data. non UTF-16 data for UTF-16 type
        projects and non ASCII data for older projects will be removed before
        dumping.

        Args:
            new_data (str): The string to be dumped to event data;

        Raises:
            TypeError: When `new_data` isn't an `str` object.
        """

        text = new_data
        if not isinstance(text, str):
            raise TypeError(f"Expected an str object; got {type(text)!r}")
        # Version event (199) is always ASCII
        if _TextEvent.uses_unicode and self.id != 199:
            self.data = text.encode("utf-16", errors="ignore") + b"\0\0"
        else:
            self.data = text.encode("ascii", errors="ignore") + b"\0"

    def to_str(self) -> str:
        if _TextEvent.uses_unicode and self.id != 199:
            return self.as_uf16(self.data)
        return self.as_ascii(self.data)

    def __repr__(self) -> str:
        return f'<{super().__repr__().strip("<>")!r}, s="{self.to_str()!r}">'

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID from \
                **192** to **207** or in `DATA_TEXT_EVENTS`.
            data (bytes): A `bytes` object.

        Raises:
            ValueError: When `id` is not in range of 192-207 or in `DATA_TEXT_EVENTS`.
        """

        if id not in range(TEXT, DATA) and id not in DATA_TEXT_EVENTS:
            raise ValueError(f"Unexpected ID: {id!r}")
        if not isinstance(data, bytes):
            raise TypeError(f"Expected a bytes object; got {type(data)!r}")
        super().__init__(id, data)


class _DataEvent(_VariableSizedEvent):
    """Represents a variable sized event used for storing a blob of data, consists
    of a collection of POD types like int, bool, float, sometimes ASCII strings.
    Its size is determined by the event and also FL version sometimes.
    The task of parsing is completely handled by one of the FLObject subclasses,
    hence no `to_*` conversion method is provided."""

    _chunk_size = None
    """Used by subclasses. Parsing is cancelled if this is
    not equal to size of bytes passed to `__init__`."""

    def dump(self, new_bytes: bytes):
        """Dumps a blob of bytes to event data as is; no conversions of any-type.
        This method is used instead of directly dumping to event data for type-safety.

        Raises:
            TypeError: When `new_bytes` isn't a `bytes` object."""

        # * Changing the length of a data event is rarely needed. Maybe only for
        # * event-in-event type of events (e.g. InsertParamsEvent, Playlist events)
        # ? Maybe make a VariableDataEvent subclass for these events?
        # * This way event data size restrictions can be enforced below.

        if not isinstance(new_bytes, bytes):
            raise TypeError(
                f"Expected a bytes object; got a {type(new_bytes)!r} object"
            )
        self.data = new_bytes

    def __init__(self, id: Union[enum.IntEnum, int], data: bytes):
        """
        Args:
            id (Union[enum.IntEnum, int]): An event ID in from **208** to **255**.
            data (bytes): A `bytes` object.

        Raises:
            ValueError: When the event ID is not in the range of 208 (`DATA`) to 255.
        """

        if id < DATA:
            raise ValueError(f"Expected an event ID from 209 to 255; got {id!r}")
        if not isinstance(data, bytes):
            raise TypeError(f"Expected a bytes object; got {type(data)!r}")
        super().__init__(id, data)
        if self._chunk_size is not None:  # pragma: no cover
            if len(data) != self._chunk_size:
                return


_DataEventType = TypeVar("_DataEventType", bound=_DataEvent)