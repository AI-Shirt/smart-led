"""Config flow: pick the ESPHome panel's show_frame action."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

from .const import CONF_FRAME_SERVICE, DOMAIN

FRAME_SUFFIX = "_show_frame"


class SmartLedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up a Smart LED display."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            service = user_input[CONF_FRAME_SERVICE]
            await self.async_set_unique_id(service)
            self._abort_if_unique_id_configured()
            name = service.removesuffix(FRAME_SUFFIX).replace("_", " ").title()
            return self.async_create_entry(title=name, data={CONF_FRAME_SERVICE: service})

        services = sorted(
            s for s in self.hass.services.async_services().get("esphome", {}) if s.endswith(FRAME_SUFFIX)
        )
        if not services:
            return self.async_abort(reason="no_panels")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_FRAME_SERVICE): SelectSelector(
                        SelectSelectorConfig(options=services, mode=SelectSelectorMode.DROPDOWN)
                    )
                }
            ),
        )
