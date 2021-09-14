import enum
from typing import Optional, ValuesView

from pyflp.flobject.flobject import FLObject
from pyflp.event import (
    Event,
    WordEvent,
    DWordEvent,
    TextEvent,
    DataEvent
)
from pyflp.flobject.plugin import *
from pyflp.utils import (
    WORD,
    DWORD,
    TEXT,
    DATA
)

@enum.unique
class InsertSlotEventID(enum.IntEnum):
    DefaultName = TEXT + 9
    PluginNew = DATA + 4    # VST/Native plugin <-> Host wrapper data, windows pos of plugin etc, currently selected plugin wrapper page; minimized, closed or not
    Icon = DWORD + 27
    Color = DWORD
    Plugin = DATA + 5         # Plugin preset data, this is what uses the most space typically
    Index = WORD + 34       # FL 12.3+, TODO: Looks like it used for storing index but not probably

class InsertSlot(FLObject):
    _count = 0      # Resets everytime a new instance of Insert is created
    max_count = 10  # TODO: Older versions had 8, maybe lesser as well

    @property
    def default_name(self) -> Optional[str]:
        """'Fruity Wrapper' for VST/AU plugins. Actual name for native plugins."""
        return getattr(self, '_default_name', None)
    
    @default_name.setter
    def default_name(self, value: str):
        self.setprop('default_name', value)
    
    @property
    def icon(self) -> Optional[int]:
        return getattr(self, '_icon', None)
    
    @icon.setter
    def icon(self, value: int):
        self.setprop('icon', value)
    
    @property
    def color(self) -> Optional[int]:
        return getattr(self, '_color', None)
    
    @color.setter
    def color(self, value: int):
        self.setprop('color', value)
    
    @property
    def index(self) -> Optional[int]:
        """Index (FL12.3+) of a slot, occurs irrespective of whether the slot is used or not."""
        return getattr(self, '_index', None)
    
    @index.setter
    def index(self, value: int):
        assert value in range(0, InsertSlot.max_count + 1)
        self.setprop('index', value)
    
    @property
    def enabled(self) -> Optional[bool]:
        return getattr(self, '_enabled', None)
    
    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value

    @property
    def mix(self) -> Optional[int]:
        """Dry/Wet mix"""
        return getattr(self, '_mix', None)

    @mix.setter
    def mix(self, value: int):
        self._mix = value
    
    @property
    def plugin(self) -> Optional[Plugin]:
        return getattr(self, '_plugin', None)
    
    @plugin.setter
    def plugin(self, value: Plugin):
        self._plugin = value

    def _parse_word_event(self, event: WordEvent) -> None:
        if event.id == InsertSlotEventID.Index:
            self._events['index'] = event
            self._index = event.to_uint16()
    
    def _parse_dword_event(self, event: DWordEvent):
        if event.id == InsertSlotEventID.Color:
            self._events['color'] = event
            self._color = event.to_uint32()
        elif event.id == InsertSlotEventID.Icon:
            self._events['icon'] = event
            self._icon = event.to_uint32()

    def _parse_text_event(self, event: TextEvent):
        if event.id == InsertSlotEventID.DefaultName:
            self._events['default_name'] = event
            self._default_name = event.to_str()
    
    def _parse_data_event(self, event: DataEvent):
        if event.id == InsertSlotEventID.PluginNew:
            self._events['new'] = event
            self._new_data = event.data
            # TODO: Parsing similar to ChannelEventID.New, infact they are same events
        elif event.id == InsertSlotEventID.Plugin:
            self._events['plugin'] = event
            if self._default_name == "Fruity soft clipper":
                self._plugin = FSoftClipper()
            self._plugin.parse(event)
    
    def save(self) -> Optional[ValuesView[Event]]:
        self._log.debug("save() called")
        _new_event = self._events.get('new')
        if _new_event:
            self._log.info(f"{InsertSlotEventID.PluginNew.name} new size: {len(self._new)} bytes")
            _new_event.dump(self._new_data)
        else:
            self._log.error(f"{InsertSlotEventID.PluginNew.name} doesn't exist, setting it is useless")
        
        _data_event = self._events.get('data')
        if _data_event:
            self._log.info(f"{InsertSlotEventID.Plugin.name} new size: {len(self._data)} bytes")
            # _data_event.dump(self._plugin.save()) TODO
        else:
            self._log.error(f"{InsertSlotEventID.Plugin.name} doesn't exist, setting it is useless")
        
        return super().save()
    
    def is_used(self) -> bool:
        """Whether a slot is used or empty. Decided by the presence of `InsertSlotEventID.New` event"""
        return True if self._events.get('new') else False

    def save(self) -> Optional[ValuesView[Event]]:
        self._log.info("save() called")
        self.plugin.save()
        return super().save()
    
    def __init__(self):
        super().__init__()
        InsertSlot._count += 1
        self._log.info(f"__init__(), count: {self._count}")
        assert InsertSlot._count <= InsertSlot.max_count, f"InsertSlot count: {InsertSlot._count}"