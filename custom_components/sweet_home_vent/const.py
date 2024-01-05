from enum import StrEnum
from homeassistant.components.modbus import (
    CALL_TYPE_REGISTER_HOLDING,
    CALL_TYPE_REGISTER_INPUT,
    CALL_TYPE_DISCRETE,
)

DOMAIN = "sweet_home_vent"

CONFIG = "config"

DEVICE_ID = "vent"

DATA_KEY_CONFIG = "config"
DATA_KEY_COORDINATOR = "coordinator"

CONFIG_KEY_HUB = "modbus_hub"
CONFIG_KEY_VENT_ADDR = "vent_addr"

OPTION_KEY_UPD_FREQ = "update_freq"
DEFAULT_UPD_FREQ = 30


class RegType(StrEnum):
    DISCRETE = CALL_TYPE_DISCRETE
    HOLDING = CALL_TYPE_REGISTER_HOLDING
    INPUT = CALL_TYPE_REGISTER_INPUT


MBS_D_FILTER = 0

MBS_I_TH1_T = 0  # Temp outside
MBS_I_TH1_H = 1  # humidity outside
MBS_I_TH2_T = 2  # Temp after heating
MBS_I_TH2_H = 3  # humidity after heating fan
MBS_I_PS = 4  # Pressure sensor
MBS_I_FAN_ON = 5  # Fan on/off
MBS_I_FAN_SPEED = 6  # Fan speed in percents
MBS_I_HEATER_ON = 7  # heater on / off
MBS_I_HEATER_LEVEL = 8  # Heater level in percents
MBS_I_HEATER_FULL = 9  # Heater connecterd directly
MBS_I_HM_ON = 10  # Humidifier on/off
MBS_I_HM_LEVEL = 11  # Level of power
MBS_I_HM_ERROR = 12  # Humidifier error
MBS_I_TH3_T = 13  # Temp after humidifier
MBS_I_TH3_H = 14  # Humidity after humidifier
MBS_I_FREE_MEMORY = 15  # Free memory

MBS_H_ENABLE = 0  # on/off ventilation
MBS_H_HM_ENABLE = 1  # on/off humidifer
MBS_H_ERR_CODE = 2  # Error code
MBS_H_AIR_LEVEL = 3  # Air capacity in percent = 0-100
MBS_H_DP_LIVING_ROOM = 4  # Damper living room
MBS_H_T_ROOM = 5  # temperature from room sensors
MBS_H_T_REQUIRED = 6  # temperature that is required
MBS_H_HM_ROOM = 7  # Humidity from room sensors
MBS_H_HM_REQUIRED = 8  # Humidity that is required


def notNone(pair):
    return pair[1] is not None
