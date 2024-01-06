from typing import Optional

from homeassistant.components.humidifier import HumidifierDeviceClass, HumidifierEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *
from .coordinator import VentDataCoordinator
from .entity import EntityDescription, VentEntity, VentEntityConfig


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_KEY_COORDINATOR]

    config = VentEntityConfig(
        description=EntityDescription(
            key="Humidifier",
            name="Humidifier",
            device_class=HumidifierDeviceClass.HUMIDIFIER,
        ),
        reg_num=MBS_H_HM_REQUIRED,
        reg_type=RegType.HOLDING,
    )
    async_add_entities([VenHumidifierEntity(coordinator, config, entry)])


class VenHumidifierEntity(VentEntity, HumidifierEntity):
    def __init__(
        self,
        coordinator: VentDataCoordinator,
        config: VentEntityConfig,
        entry: ConfigEntry,
    ):
        super().__init__(coordinator, config, entry)
        self._attr_supported_features = 0

    async def async_turn_on(self, **kwargs):
        await self.coordinator.writeRegister(MBS_H_HM_ENABLE, 1)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.writeRegister(MBS_H_HM_ENABLE, 0)

    async def async_set_humidity(self, humidity):
        await self.coordinator.writeRegister(self._reg_num, humidity * 10)

    @property
    def current_humidity(self):
        return self.coordinator.data[RegType.INPUT][MBS_I_HM_LEVEL] / 10.0

    @property
    def target_humidity(self):
        return self.coordinator.data[self._reg_type][self._reg_num] / 10.0

    @property
    def is_on(self):
        return self.coordinator.data[RegType.HOLDING][MBS_H_HM_ENABLE] > 0
