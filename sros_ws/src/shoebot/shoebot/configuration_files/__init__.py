
from .Echo import *
from .Wheels import *

CONFIGURATIONS = {
    frozenset({0x00}): Echo,
    frozenset({0x01, 0x02}): Wheels
}

PARTIAL_CONFIGURATIONS = {
    frozenset({0x01}): "Partial wheels configuration, missing at least one instance of device id 0x02",
    frozenset({0x02}): "Partial wheels configuration, missing at least one instance of device id 0x01"
}