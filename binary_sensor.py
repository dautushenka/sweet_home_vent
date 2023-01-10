from homeassistant.components.binary_sensor import (
    DEVICE_CLASSES_SCHEMA,
    PLATFORM_SCHEMA,
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.const import CONF_DEVICE_CLASS
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


_LOGGER = logging.getLogger(__name__)

from .const import (
    CONF_ADDRESS,
    CONF_PIN,
    DOMAIN,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_ADDRESS): cv.string,
        vol.Required(CONF_PIN): cv.string,
        vol.Optional(CONF_DEVICE_CLASS): DEVICE_CLASSES_SCHEMA,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    address = config[CONF_ADDRESS]
    pin = config[CONF_PIN]

    add_entities(
        [
            SweetHomeBinarySensor(
                int(address, 16),
                int(pin)
            )
        ],
        True,
    )

class SweetHomeBinarySensor(BinarySensorEntity):
    address: int = None
    pin: int = None
    def __init__(self, address: int, pin: int) -> None:
        super().__init__()
        self.address = address
        self.pin = pin
        self._attr_device_class = BinarySensorDeviceClass.DOOR
        self._attr_unique_id = "{}-{}-{}".format(DOMAIN, hex(address), pin)
        self._attr_name = "Binary sensor {}-{}".format(hex(address), pin)

        from .mcp23017 import addBynarySensor
        addBynarySensor(self)

    def should_poll(self) -> bool:
        return False

    def onChange(self, value: int) -> None:
        self._attr_is_on = value > 0
        self.schedule_update_ha_state()
        pass