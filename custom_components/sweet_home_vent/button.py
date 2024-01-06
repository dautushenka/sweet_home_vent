from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *
from .entity import EntityDescription, VentEntity, VentEntityConfig


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_KEY_COORDINATOR]

    config = VentEntityConfig(
        description=EntityDescription(
            key="earse_error",
            name="Earse error",
            device_class=ButtonDeviceClass.RESTART,
        ),
        reg_num=MBS_H_ERR_CODE,
        reg_type=RegType.HOLDING,
    )
    async_add_entities([VenButtonEntity(coordinator, config, entry)])


class VenButtonEntity(VentEntity, ButtonEntity):
    async def async_press(self) -> None:
        await self.coordinator.async_earseError()
