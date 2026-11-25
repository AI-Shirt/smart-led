"""Smart LED: a virtual 12x10 display in Home Assistant, mirrored by an ESPHome LED panel."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.color import color_name_to_rgb

from .canvas import RGB, Canvas
from .const import (
    ATTR_COLOR,
    ATTR_DISPLAY,
    ATTR_LINE,
    CONF_FRAME_SERVICE,
    DOMAIN,
    LINE_ROWS,
    SLOT_COLUMNS,
    WIDTH,
)
from .font import GLYPH_HEIGHT

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_SHOW_TEXT = "show_text"
SERVICE_CLEAR = "clear"

DEFAULT_COLOR = (255, 255, 255)


def _slot(value: Any) -> str:
    """A slot holds one character; empty or missing means blank."""
    if value is None:
        return " "
    text = str(value)
    if len(text) > 1:
        raise vol.Invalid(f"a slot holds one character, got '{text}'")
    return text or " "


def _color(value: Any) -> RGB:
    """Accept a colour name ('red'), hex ('#FF8000' or 'FF8000') or [r, g, b]."""
    if isinstance(value, (list, tuple)):
        if len(value) != 3:
            raise vol.Invalid("an RGB colour needs 3 values")
        r, g, b = (int(c) for c in value)
        if not all(0 <= c <= 255 for c in (r, g, b)):
            raise vol.Invalid("RGB values must be 0-255")
        return (r, g, b)
    text = str(value).strip()
    hex_text = text.lstrip("#")
    if len(hex_text) == 6:
        try:
            v = int(hex_text, 16)
            return ((v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF)
        except ValueError:
            pass
    try:
        return tuple(color_name_to_rgb(text))  # type: ignore[return-value]
    except ValueError as err:
        raise vol.Invalid(f"unknown colour '{text}'") from err


SHOW_TEXT_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DISPLAY): cv.string,
        vol.Required(ATTR_LINE): vol.In(list(LINE_ROWS)),
        vol.Optional("left"): _slot,
        vol.Optional("separator"): _slot,
        vol.Optional("right"): _slot,
        vol.Optional(ATTR_COLOR, default=DEFAULT_COLOR): _color,
        vol.Optional("left_color"): _color,
        vol.Optional("separator_color"): _color,
        vol.Optional("right_color"): _color,
    }
)

CLEAR_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DISPLAY): cv.string,
        vol.Optional(ATTR_LINE, default="all"): vol.In([*LINE_ROWS, "all"]),
    }
)


class Display:
    """One smart-led panel: a canvas plus the ESPHome action that shows it."""

    def __init__(self, hass: HomeAssistant, frame_service: str) -> None:
        self.hass = hass
        self.frame_service = frame_service
        self.canvas = Canvas()

    async def async_push(self) -> None:
        await self.hass.services.async_call(
            "esphome",
            self.frame_service,
            {"pixels": self.canvas.to_hex()},
            blocking=True,
        )


def _display_for(hass: HomeAssistant, call: ServiceCall) -> Display:
    displays: dict[str, Display] = hass.data.get(DOMAIN, {})
    entry_id = call.data.get(ATTR_DISPLAY)
    if entry_id:
        if entry_id not in displays:
            raise ServiceValidationError(f"Smart LED display '{entry_id}' not found")
        return displays[entry_id]
    if len(displays) == 1:
        return next(iter(displays.values()))
    if not displays:
        raise ServiceValidationError("No Smart LED display is set up")
    raise ServiceValidationError("Several Smart LED displays are set up; pick one with 'display'")


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})

    async def show_text(call: ServiceCall) -> None:
        display = _display_for(hass, call)
        y0 = LINE_ROWS[call.data[ATTR_LINE]]
        base = call.data[ATTR_COLOR]
        display.canvas.fill_rect(0, y0, WIDTH, GLYPH_HEIGHT, (0, 0, 0))
        for slot, x0 in SLOT_COLUMNS.items():
            char = call.data.get(slot, " ")
            display.canvas.draw_char(char, x0, y0, call.data.get(f"{slot}_color", base))
        await display.async_push()

    async def clear(call: ServiceCall) -> None:
        display = _display_for(hass, call)
        line = call.data[ATTR_LINE]
        if line == "all":
            display.canvas.clear()
        else:
            display.canvas.fill_rect(0, LINE_ROWS[line], WIDTH, GLYPH_HEIGHT, (0, 0, 0))
        await display.async_push()

    hass.services.async_register(DOMAIN, SERVICE_SHOW_TEXT, show_text, schema=SHOW_TEXT_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_CLEAR, clear, schema=CLEAR_SCHEMA)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = Display(hass, entry.data[CONF_FRAME_SERVICE])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
