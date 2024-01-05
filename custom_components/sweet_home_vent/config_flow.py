from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.modbus import get_hub
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONFIG_KEY_HUB,
    CONFIG_KEY_VENT_ADDR,
    DEFAULT_UPD_FREQ,
    DOMAIN,
    OPTION_KEY_UPD_FREQ,
)


def _getFormFields(user_input: dict[str, Any]) -> dict:
    user_input = {} if user_input is None else user_input
    return {
        vol.Required(CONFIG_KEY_HUB, default=user_input.get(CONFIG_KEY_HUB, "")): str,
        vol.Required(
            CONFIG_KEY_VENT_ADDR, default=user_input.get(CONFIG_KEY_VENT_ADDR, "")
        ): vol.All(int, vol.Range(min=1)),
        vol.Required(
            OPTION_KEY_UPD_FREQ, default=user_input.get(OPTION_KEY_UPD_FREQ, "")
        ): vol.All(int, vol.Range(min=10)),
    }


def _getFormData(
    hass: HomeAssistant, user_input: dict[str, Any] | None = None
) -> dict[str, Any]:
    result = {
        "data_schema": vol.Schema(_getFormFields(user_input if not None else {})),
        "errors": {},
    }
    if user_input is None or len(user_input) < 1:
        return result

    try:
        get_hub(hass, user_input[CONFIG_KEY_HUB])
    except KeyError:
        result.get("errors")[CONFIG_KEY_HUB] = "Invalid modbus hub"

    return result

    # vol.validate(user_input)

    # if user_input[CONFIG_KEY_VENT_ADDR] < 1:
    #     # TODO validate with schema
    #     errors[CONFIG_KEY_VENT_ADDR] = "Invalid address"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        form = _getFormData(self.hass, user_input)
        if user_input is None or len(form.get("errors")) > 0:
            return self.async_show_form(
                step_id="user",
                **form,
            )

        await self.async_set_unique_id(
            f"{user_input[CONFIG_KEY_HUB]}-{user_input[CONFIG_KEY_VENT_ADDR]}"
        )
        self._abort_if_unique_id_configured()
        options = {}
        options[OPTION_KEY_UPD_FREQ] = DEFAULT_UPD_FREQ

        return self.async_create_entry(title="Ventilation", data={}, options=user_input)

    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        t = self.config_entry.options
        """Manage the options."""
        form = _getFormData(
            self.hass,
            user_input if user_input is not None else dict(self.config_entry.options),
        )
        if user_input is None or len(form.get("errors")) > 0:
            return self.async_show_form(
                step_id="init",
                **form,
            )
        await self.hass.config_entries.async_reload(self.config_entry.entry_id)

        return self.async_create_entry(title="", data=user_input)
