from config.custom_components.sweet_home_vent.coordinator import VentDataCoordinator

from homeassistant.components.cover import (
    CoverEntityDescription,
    CoverEntity,
    CoverEntityFeature,
    CoverDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *
from .entity import VentEntity, VentEntityConfig


class VentCoverConfig(VentEntityConfig):
    description: CoverEntityDescription
    features: CoverEntityFeature | None


COVERS: tuple[VentCoverConfig, ...] = (
    VentCoverConfig(
        description=CoverEntityDescription(
            key="living_room_damper",
            name="Living room damper",
            device_class=CoverDeviceClass.DAMPER,
        ),
        reg_num=MBS_H_DP_LIVING_ROOM,
        reg_type=RegType.HOLDING,
        features=CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_KEY_COORDINATOR]

    sensors = []
    for config in COVERS:
        args = {}
        args["has_entity_name"] = True

        args.update(dict(filter(notNone, config["description"].__dict__.items())))

        config["description"] = CoverEntityDescription(**args)
        sensors.append(VentCover(coordinator, config, entry))

    async_add_entities(sensors)


class VentCover(VentEntity, CoverEntity):
    def __init__(
        self,
        coordinator: VentDataCoordinator,
        config: VentCoverConfig,
        entry: ConfigEntry,
    ):
        super().__init__(coordinator, config, entry)
        self._attr_supported_features = config["features"]

    async def async_open_cover(self, **kwargs):
        await self.coordinator.writeRegister(self._reg_num, 0)

    async def async_close_cover(self, **kwargs):
        await self.coordinator.writeRegister(self._reg_num, 1)

    @property
    def is_closed(self):
        return self.coordinator.data[self._reg_type][self._reg_num] > 0
