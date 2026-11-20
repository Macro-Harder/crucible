"""Crucible product package.

The package surface carries the slice modules. MOD-01, types and
validation, stands in mod01; its public surface is re-exported here.

Surface guide, in short. The package carries fifteen modules,
mod01 to mod14 and mod16, exporting 660 names in total on the
summed basis. mod01 Types and validation; mod02 Seed and Stream
Engine; mod03 Society Generator; mod04 Tick Engine; mod05 Parley
Core; mod06 Escrow Core; mod07 Escrow Adapter; mod08 Detection
Layer; mod09 Attacker Seat; mod10 Recorder and stores; mod11
Reporter; mod12 Sweep Controller; mod13 Replication Checker;
mod14 Shell; mod16 Integration surface.

User entry points: the mod01 record and validation acts
re-exported here, the FORM_TYPES classes, and the mod10 store
acts. Internal surface: every name beginning with an underscore
in any module, and the helper machinery behind the entry points.
The README at the package root states the guide in full, and
states that executable runs stand gated on DQ7-02.
"""

from . import mod01
from .mod01 import *  # noqa: F401,F403
from .mod01 import __all__ as _mod01_all

__all__ = ["mod01"] + list(_mod01_all)
