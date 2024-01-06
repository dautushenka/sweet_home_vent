from typing import TypedDict

from homeassistant.components.sensor import EntityDescription  # noqa: D100
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, RegType
from .coordinator import VentDataCoordinator


class VentEntityConfig(TypedDict):
    description: EntityDescription
    reg_num: int
    reg_type: RegType


class VentEntity(CoordinatorEntity[VentDataCoordinator], Entity):
    _reg_type: RegType
    _reg_num: int

    def __init__(
        self,
        coordinator: VentDataCoordinator,
        config: VentEntityConfig,
        entry: ConfigEntry,
    ):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)

        self._reg_type = config.get("reg_type")
        self._reg_num = config.get("reg_num")
        self.entity_description = config.get("description")
        self._attr_unique_id = f"{self._reg_type}-{self._reg_num}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )
