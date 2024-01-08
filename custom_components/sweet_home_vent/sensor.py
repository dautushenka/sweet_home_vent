from enum import StrEnum
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfInformation,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *
from .coordinator import VentDataCoordinator
from .entity import VentEntity, VentEntityConfig

_LOGGER = logging.getLogger(__name__)


class SensorType(StrEnum):
    TEMPERATURE = "temparature"
    HUMIDITY = "humidity"
    HEATER = "heater"
    OTHER = "other"


class VentSensorConfig(VentEntityConfig):
    description: SensorEntityDescription
    type: SensorType


SENSORS: tuple[VentSensorConfig, ...] = (
    VentSensorConfig(
        description=SensorEntityDescription(
            key="temperature_sensor",
            name="Temperature outside",
        ),
        reg_num=MBS_I_TH1_T,
        reg_type=RegType.INPUT,
        type=SensorType.TEMPERATURE,
    ),
    VentSensorConfig(
        description=SensorEntityDescription(
            key="humidity_sensor",
            name="Humidity outside",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            has_entity_name=True,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        reg_num=MBS_I_TH1_H,
        reg_type=RegType.INPUT,
        type=SensorType.HUMIDITY,
    ),
    VentSensorConfig(
        description=SensorEntityDescription(
            key="temperature_sensor",
            name="Temperature airduct",
        ),
        reg_num=MBS_I_TH2_T,
        reg_type=RegType.INPUT,
        type=SensorType.TEMPERATURE,
    ),
    VentSensorConfig(
        description=SensorEntityDescription(
            key="humidity_sensor",
            name="Humidity airduct",
        ),
        reg_num=MBS_I_TH2_H,
        reg_type=RegType.INPUT,
        type=SensorType.HUMIDITY,
    ),
    VentSensorConfig(
        description=SensorEntityDescription(
            key="temperature_sensor",
            name="Temperature final",
        ),
        reg_num=MBS_I_TH3_T,
        reg_type=RegType.INPUT,
        type=SensorType.TEMPERATURE,
    ),
    VentSensorConfig(
        description=SensorEntityDescription(
            key="humidity_sensor",
            name="Humidity final",
        ),
        reg_num=MBS_I_TH3_H,
        reg_type=RegType.INPUT,
        type=SensorType.HUMIDITY,
    ),
    VentSensorConfig(
        description=SensorEntityDescription(
            key="pressure",
            name="Air pressure",
            device_class=SensorDeviceClass.PRESSURE,
            native_unit_of_measurement=UnitOfPressure.PA,
        ),
        reg_num=MBS_I_PS,
        reg_type=RegType.INPUT,
        type=SensorType.OTHER,
    ),
    VentSensorConfig(
        description=SensorEntityDescription(
            key="air_level",
            name="Air level",
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
        ),
        reg_num=MBS_I_FAN_SPEED,
        reg_type=RegType.INPUT,
        type=SensorType.OTHER,
    ),
    VentSensorConfig(
        description=SensorEntityDescription(
            key="heater_level",
            name="Heater level",
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
        ),
        reg_num=MBS_I_HEATER_LEVEL,
        reg_type=RegType.INPUT,
        type=SensorType.HEATER,
    ),
    VentSensorConfig(
        description=SensorEntityDescription(
            key="humudity_level",
            name="Humudity level",
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
        ),
        reg_num=MBS_I_HM_LEVEL,
        reg_type=RegType.INPUT,
        type=SensorType.OTHER,
    ),
    VentSensorConfig(
        description=SensorEntityDescription(
            key="free_memory",
            name="Free memory",
            native_unit_of_measurement=UnitOfInformation.BYTES,
            device_class=SensorDeviceClass.DATA_SIZE,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        reg_num=MBS_I_FREE_MEMORY,
        reg_type=RegType.INPUT,
        type=SensorType.OTHER,
    ),
)


def notNone(pair):
    return pair[1] is not None


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    _LOGGER.info("Start setupping sensor platform")
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_KEY_COORDINATOR]

    sensors = []
    for config in SENSORS:
        args = {}
        args["has_entity_name"] = True
        args["state_class"] = SensorStateClass.MEASUREMENT
        Sensor = VentSensor
        if config["type"] == SensorType.TEMPERATURE:
            args["device_class"] = SensorDeviceClass.TEMPERATURE
            args["native_unit_of_measurement"] = UnitOfTemperature.CELSIUS
            Sensor = VentTemperatureSensor
        elif config["type"] == SensorType.HUMIDITY:
            args["device_class"] = SensorDeviceClass.HUMIDITY
            args["native_unit_of_measurement"] = PERCENTAGE
            Sensor = VentHumiditySensor
        elif config["type"] == SensorType.HEATER:
            Sensor = VentHeaterSensor

        args.update(dict(filter(notNone, config["description"].__dict__.items())))

        config["description"] = SensorEntityDescription(**args)
        sensors.append(Sensor(coordinator, config, entry))

    async_add_entities(sensors)


class VentSensor(VentEntity, SensorEntity):
    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._reg_type][self._reg_num]


class VentTemperatureSensor(VentEntity, SensorEntity):
    @property
    def native_value(self):
        value = self.coordinator.data[self._reg_type][self._reg_num]
        if value > 1000:
            return (value - 65535) / 10.0

        return value / 10.0


class VentHumiditySensor(VentEntity, SensorEntity):
    @property
    def native_value(self):
        value = self.coordinator.data[self._reg_type][self._reg_num]

        return value / 10.0


class VentHeaterSensor(VentEntity, SensorEntity):
    @property
    def native_value(self):
        isOn = self.coordinator.data[RegType.INPUT][MBS_I_HEATER_ON] > 0
        isFull = self.coordinator.data[RegType.INPUT][MBS_I_HEATER_FULL] > 0
        value = self.coordinator.data[self._reg_type][self._reg_num]

        if not isOn:
            return 0
        if isFull:
            return 100

        return value
