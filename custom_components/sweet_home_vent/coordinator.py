from datetime import timedelta
import logging

from homeassistant.components.modbus import (
    CALL_TYPE_DISCRETE,
    CALL_TYPE_REGISTER_HOLDING,
    CALL_TYPE_REGISTER_INPUT,
    ModbusHub,
    get_hub,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import *

_LOGGER = logging.getLogger(__name__)

CALL_TYPE_WRITE_REGISTER = "write_register"


class VentDataCoordinator(DataUpdateCoordinator):
    _hub: ModbusHub
    _addr: int

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Coordinator",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(
                seconds=config_entry.options[OPTION_KEY_UPD_FREQ]
            ),
        )
        self._hub = get_hub(hass, config_entry.options[CONFIG_KEY_HUB])
        self._addr = config_entry.options[CONFIG_KEY_VENT_ADDR]
        self.data: dict[RegType, list] = {
            RegType.INPUT: [],
            RegType.HOLDING: [],
            RegType.DISCRETE: [],
        }

    async def writeRegister(
        self, register: int, value: int, refresh: bool = True
    ) -> bool:
        result = await self._hub.async_pb_call(
            self._addr, register, value, CALL_TYPE_WRITE_REGISTER
        )

        if refresh:
            await self._async_refresh()

        if not result:
            return False
        return True

    async def async_earseError(self) -> bool:
        return await self.writeRegister(MBS_H_ERR_CODE, 0)

    async def _async_update_data(self):
        data: dict[RegType, list] = {}
        result = await self._hub.async_pb_call(
            self._addr, 0, 16, CALL_TYPE_REGISTER_INPUT
        )
        if not result:
            _LOGGER.warning("Fail to get input registers")
            raise UpdateFailed("Error communicating with device")

        data[RegType.INPUT] = result.registers

        result = await self._hub.async_pb_call(
            self._addr, 0, 9, CALL_TYPE_REGISTER_HOLDING
        )
        if not result:
            _LOGGER.warning("Fail to get holding registers")
            raise UpdateFailed("Error communicating with device")

        data[RegType.HOLDING] = result.registers

        result = await self._hub.async_pb_call(self._addr, 0, 1, CALL_TYPE_DISCRETE)
        if not result:
            _LOGGER.warning("Fail to get descrete registers")
            raise UpdateFailed("Error communicating with device")

        data[RegType.DISCRETE] = result.bits

        return data
