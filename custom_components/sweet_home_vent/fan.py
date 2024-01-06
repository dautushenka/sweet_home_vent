import logging
from typing import Optional

from config.custom_components.sweet_home_vent.coordinator import VentDataCoordinator
from homeassistant.components.fan import (
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *
from .entity import VentEntity, VentEntityConfig

_LOGGER = logging.getLogger(__name__)


class VentFanConfig(VentEntityConfig):
    description: FanEntityDescription
    features: FanEntityFeature | None


FANS: tuple[VentFanConfig, ...] = (
    VentFanConfig(
        description=FanEntityDescription(
            key="required_air_level",
            name="Air",
        ),
        reg_num=MBS_H_AIR_LEVEL,
        reg_type=RegType.HOLDING,
        features=FanEntityFeature.SET_SPEED,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_KEY_COORDINATOR]
    _LOGGER.info("Start setupping fan platform")

    sensors = []
    for config in FANS:
        args = {}
        args["has_entity_name"] = True

        args.update(dict(filter(notNone, config["description"].__dict__.items())))

        config["description"] = FanEntityDescription(**args)
        sensors.append(VentFanEntity(coordinator, config, entry))

    _LOGGER.debug("Adding fan entity")
    async_add_entities(sensors)


class VentFanEntity(VentEntity, FanEntity):
    def __init__(
        self,
        coordinator: VentDataCoordinator,
        config: VentFanConfig,
        entry: ConfigEntry,
    ):
        super().__init__(coordinator, config, entry)
        self._attr_supported_features = config["features"]

    async def async_turn_on(
        self, speed: Optional[str] = None, percentage: Optional[int] = None
    ) -> None:
        if self.coordinator.data[RegType.HOLDING][MBS_H_ERR_CODE] > 0:
            return

        if percentage is not None:
            await self.coordinator.writeRegister(self._reg_num, percentage, False)

        await self.coordinator.writeRegister(MBS_H_ENABLE, 1)

    async def async_turn_off(self) -> None:
        await self.coordinator.writeRegister(MBS_H_ENABLE, 0)

    async def async_set_percentage(self, percentage: int) -> None:
        await self.coordinator.writeRegister(self._reg_num, percentage)

    @property
    def percentage(self):
        return self.coordinator.data[self._reg_type][self._reg_num]

    @property
    def is_on(self):
        return self.coordinator.data[RegType.HOLDING][MBS_H_ENABLE] > 0
