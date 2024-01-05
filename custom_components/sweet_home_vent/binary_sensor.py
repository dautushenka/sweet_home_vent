from config.custom_components.sweet_home_vent.coordinator import VentDataCoordinator
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *
from .entity import VentEntity, VentEntityConfig

SENSORS: tuple[VentEntityConfig, ...] = (
    VentEntityConfig(
        description=BinarySensorEntityDescription(
            key="humidifier_on_off",
            name="Humidifier",
            device_class=BinarySensorDeviceClass.POWER,
        ),
        reg_num=MBS_I_HM_ON,
        reg_type=RegType.INPUT,
    ),
    VentEntityConfig(
        description=BinarySensorEntityDescription(
            key="heater_on_off",
            name="Heater",
            device_class=BinarySensorDeviceClass.POWER,
        ),
        reg_num=MBS_I_HEATER_ON,
        reg_type=RegType.INPUT,
    ),
    VentEntityConfig(
        description=BinarySensorEntityDescription(
            key="heater_full",
            name="Heater full power",
            device_class=BinarySensorDeviceClass.POWER,
        ),
        reg_num=MBS_I_HEATER_FULL,
        reg_type=RegType.INPUT,
    ),
    VentEntityConfig(
        description=BinarySensorEntityDescription(
            key="humidifier_error",
            name="Humidifier error",
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        reg_num=MBS_I_HM_ERROR,
        reg_type=RegType.INPUT,
    ),
    VentEntityConfig(
        description=BinarySensorEntityDescription(
            key="Filter",
            name="Filter",
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        reg_num=MBS_D_FILTER,
        reg_type=RegType.DISCRETE,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_KEY_COORDINATOR]

    sensors = []
    for config in SENSORS:
        sensors.append(VentBinarySensor(coordinator, config, entry))

    sensors.append(
        VentErrorBinarySensor(
            coordinator,
            VentEntityConfig(
                description=BinarySensorEntityDescription(
                    key="Error",
                    name="Error",
                    device_class=BinarySensorDeviceClass.PROBLEM,
                    entity_category=EntityCategory.DIAGNOSTIC,
                ),
                reg_num=MBS_H_ERR_CODE,
                reg_type=RegType.HOLDING,
            ),
            entry,
        )
    )

    async_add_entities(sensors)


class VentBinarySensor(VentEntity, BinarySensorEntity):
    def __init__(
        self,
        coordinator: VentDataCoordinator,
        config: VentEntityConfig,
        entry: ConfigEntry,
    ):
        super().__init__(coordinator, config, entry)
        self._attr_has_entity_name = True

    @property
    def is_on(self):
        return int(self.coordinator.data[self._reg_type][self._reg_num]) > 0


class VentErrorBinarySensor(VentEntity, BinarySensorEntity):
    def __init__(
        self,
        coordinator: VentDataCoordinator,
        config: VentEntityConfig,
        entry: ConfigEntry,
    ):
        super().__init__(coordinator, config, entry)
        self._attr_has_entity_name = True
        self._async_update_attrs()

    @property
    def is_on(self):
        return int(self.coordinator.data[self._reg_type][self._reg_num]) > 0

    def _convertCodeToMessage(self) -> str:
        errCode = self.coordinator.data[self._reg_type][self._reg_num]
        if errCode < 1:
            return ""

        modules = [
            "UNKNOWN",  # 0
            "MAIN",  # 1
            "TH1",  # 2
            "TH2",  # 3
            "TH3",  # 4
            "PS",  # 5
            "CL2MB",  # 6
            "FAN",  # 7
            "HEATER",  # 8
            "BOARD",  # 9
            "HM",  # 10
            "RM",  # 11
            "MBQ",  # 12
            "MBS",  # 13
            "VENT",  # 14
        ]
        errCodes = [
            "NO_ERROR",  # 0
            "Fail i2c setup"  # I2C_SETUP,      // 1
            "Temp or humidity out of range"  # VALUE_OUTRANGE, // 2
            "Modbus connection request fail more than 10 times"  # MB_FAIL,        // 3
            "Fan does not pressurize enough air"  # FAN_FAIL,       // 4
            "Humidity is not updated more than 7 min"  # HUMUDITY_UPDATE_FAIL, // 5
            "UNKOWN",
        ]

        module = modules[errCode >> 8]
        error = errCode & 0xFF

        return f"{module}: {error}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update attributes when the coordinator updates."""
        self._async_update_attrs()
        super()._handle_coordinator_update()

    @callback
    def _async_update_attrs(self) -> None:
        self._attr_extra_state_attributes = {
            "error": self._convertCodeToMessage(),
            "error_code": int(self.coordinator.data[self._reg_type][self._reg_num]),
        }
