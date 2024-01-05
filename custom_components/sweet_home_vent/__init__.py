from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_IDENTIFIERS, ATTR_MANUFACTURER, ATTR_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntry

from .const import DATA_KEY_COORDINATOR, DOMAIN
from .coordinator import VentDataCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.COVER,
    Platform.FAN,
    Platform.HUMIDIFIER,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Start setuping entry")
    hass.data.setdefault(DOMAIN, {})
    # hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    params = {
        ATTR_IDENTIFIERS: {(DOMAIN, entry.entry_id)},
        ATTR_MANUFACTURER: "dautushenka",
        ATTR_NAME: "Ventilation",
    }
    dr.async_get(hass).async_get_or_create(config_entry_id=entry.entry_id, **params)

    coordinator = VentDataCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN][entry.entry_id][DATA_KEY_COORDINATOR] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # async_add_entities(
    #     MyEntity(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    # )

    # hass.async_add_job(hass.config_entries.flow.async_init(
    #     DOMAIN
    # ))

    return True


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return True
