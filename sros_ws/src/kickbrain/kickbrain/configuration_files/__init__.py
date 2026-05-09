
from .Echo import *
from .Wheels import *

CONFIGURATIONS = {
    frozenset({0x00, 0x01}): Echo,
    frozenset({0x00, 0x02, 0x03}): Wheels
}

PARTIAL_CONFIGURATIONS = {
    frozenset({0x00}): "No devices connected",
    frozenset({0x00, 0x02}): "Partial wheels configuration, missing at least one instance of device id 0x02",
    frozenset({0x00, 0x03}): "Partial wheels configuration, missing at least one instance of device id 0x01"
}