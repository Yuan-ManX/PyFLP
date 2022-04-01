import enum
from typing import Any

from bytesioex import BytesIOEx

from pyflp._event import _DataEvent
from pyflp._flobject import _FLObject
from pyflp._properties import _BoolProperty, _EnumProperty, _IntProperty, _UIntProperty
from pyflp._validators import _IntValidator, _UIntValidator

__all__ = ["ChannelEnvelopeLFO", "ChannelEnvelopeLFOEvent"]

EnvelopeLFONames = ("Panning", "Volume", "Pitch", "Mod X", "Mod Y")


class ChannelEnvelopeLFOEvent(_DataEvent):
    _chunk_size = 68

    def __init__(self, data: bytes):
        from pyflp.channel.channel import Channel

        super().__init__(Channel.EventID.EnvelopeLFO, data)
        self.__r = r = BytesIOEx(data)
        self.__flags = ChannelEnvelopeLFO._Flags(r.read_I())  # 4
        self.lfo_synced = False
        if ChannelEnvelopeLFO._Flags.LFOTempoSync in self.__flags:
            self.lfo_synced = True
        self.lfo_retrig = False
        if ChannelEnvelopeLFO._Flags.LFORetrig in self.__flags:
            self.lfo_retrig = True
        self.enabled = True if r.read_i() == -1 else False  # 8
        self.env_predelay = r.read_I()  # 12
        self.env_attack = r.read_I()  # 16
        self.env_hold = r.read_I()  # 20
        self.env_decay = r.read_I()  # 24
        self.env_sustain = r.read_I()  # 28
        self.env_release = r.read_I()  # 32
        r.seek(52)
        self.lfo_shape = ChannelEnvelopeLFO.LFOShape(r.read_I())  # 56
        self.env_att_tns = r.read_i()  # 60
        self.env_sus_tns = r.read_i()  # 64
        self.env_rel_tns = r.read_i()  # 68

    def dump(self, n: str, v: Any):
        r = self.__r
        if n in ("lfo_synced", "lfo_retrig"):
            r.seek(0)
            if n == "lfo_synced":
                f = ChannelEnvelopeLFO._Flags.LFOTempoSync
                if v:
                    self.__flags |= f
                else:
                    self.__flags &= ~f
            else:
                f = ChannelEnvelopeLFO._Flags.LFORetrig
                if v:
                    self.__flags |= f
                else:
                    self.__flags &= ~f
            r.write_I(self.__flags)
        elif n == "enabled":
            r.seek(4)
            if v:
                r.write_i(-1)
            else:
                r.write_i(0)
        elif n == "env_predelay":
            r.seek(8)
            r.write_I(v)
        elif n == "env_attack":
            r.seek(12)
            r.write_I(v)
        elif n == "env_hold":
            r.seek(16)
            r.write_I(v)
        elif n == "env_decay":
            r.seek(20)
            r.write_I(v)
        elif n == "env_sustain":
            r.seek(24)
            r.write_I(v)
        elif n == "env_release":
            r.seek(28)
            r.write_I(v)
        elif n == "lfo_shape":
            r.seek(52)
            r.write_I(v)
        elif n == "env_att_tns":
            r.seek(56)
            r.write_i(v)
        elif n == "env_sus_tns":
            r.seek(60)
            r.write_i(v)
        elif n == "env_rel_tns":
            r.seek(64)
            r.write_i(v)
        r.seek(0)
        super().dump(r.read())


class ChannelEnvelopeLFO(_FLObject):
    """Used by `Channel._env_lfos`.

    [Manual](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/chansettings_ins.htm)"""

    _AHDSR_VALIDATOR = _IntValidator(100, 65536)
    _TNS_VALIDATOR = _IntValidator(-128, 128)

    @enum.unique
    class LFOShape(enum.IntEnum):
        """See `ChannelEnvelope.lfo_shape`."""

        Sine = 0
        Triangle = 1
        Pulse = 2

    @enum.unique
    class _Flags(enum.IntFlag):
        """See `ChannelEnvelope.flags`."""

        LFOTempoSync = 1 << 1
        """See `ChannelEnvelope.lfo_synced`."""

        Unknown = 1 << 2
        """Occurs for volume envlope only."""

        LFORetrig = 1 << 5
        """See `ChannelEnvelope.lfo_retrig`."""

    def _setprop(self, n, v):
        self.__cel.dump(n, v)
        super()._setprop(n, v)

    lfo_synced: bool = _BoolProperty()
    """Whether LFO is synced with tempo."""

    lfo_retrig: bool = _BoolProperty()
    """Whether LFO is in retriggered mode."""

    enabled: bool = _BoolProperty()

    env_predelay: int = _UIntProperty(_AHDSR_VALIDATOR)
    """Envelope predelay time. Min: 100 (0%), Max: 65536 (100%), Default: 100 (0%)."""

    env_attack: int = _UIntProperty(_AHDSR_VALIDATOR)
    """Envelope attack time. Min: 100 (0%), Max: 65536 (100%), Default: 20000 (31%)."""

    env_hold: int = _UIntProperty(_AHDSR_VALIDATOR)
    """Envelope hold time. Min: 100 (0%), Max: 65536 (100%), Default: 20000 (31%)."""

    env_decay: int = _UIntProperty(_AHDSR_VALIDATOR)
    """Envelope decay time. Min: 100 (0%), Max: 65536 (100%), Default: 30000 (46%)."""

    env_sustain: int = _UIntProperty(_UIntValidator(128))
    """Envelope sustain time. Min: 0 (0%), Max: 128 (100%), Default: 50 (39%)."""

    env_release: int = _UIntProperty(_AHDSR_VALIDATOR)
    """Envelope release time. Min: 100 (0%), Max: 65536 (100%), Default: 20000 (31%)."""

    lfo_shape: LFOShape = _EnumProperty(LFOShape)
    """LFO Shape (sine, triangle or pulse).
    See `LFOShape`. Default: `LFOShape.Sine`."""

    env_att_tns: int = _IntProperty(_TNS_VALIDATOR)
    """Envelope attack tension. Min: -128 (-100%), Max: 128 (100%), Default: 0 (0%)."""

    env_sus_tns: int = _IntProperty(_TNS_VALIDATOR)
    """Envelope sustain tension. Min: -128 (-100%), Max: 128 (100%), Default: 0 (0%)."""

    env_rel_tns: int = _IntProperty(_TNS_VALIDATOR)
    """Envelope release tension. Min: -128 (-100%),
    Max: 128 (100%), Default: -101 / 0 (-79% / 0%)."""

    def _parse_data_event(self, e: ChannelEnvelopeLFOEvent) -> None:
        self.__cel = self._events["envlfo"] = e
        self._lfo_synced = e.lfo_synced
        self._lfo_retrig = e.lfo_retrig
        self._enabled = e.enabled
        self._env_predelay = e.env_predelay
        self._env_attack = e.env_attack
        self._env_hold = e.env_hold
        self._env_decay = e.env_decay
        self._env_sustain = e.env_sustain
        self._env_release = e.env_release
        self._lfo_shape = e.lfo_shape
        self._env_att_tns = e.env_att_tns
        self._env_sus_tns = e.env_sus_tns
        self._env_rel_tns = e.env_rel_tns
