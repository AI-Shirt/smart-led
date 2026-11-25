"""Tests for the Smart LED integration."""

import pytest
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.smart_led.canvas import Canvas
from custom_components.smart_led.const import DOMAIN

FRAME_SERVICE = "led_display_show_frame"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


def render(hex_frame: str) -> list[str]:
    """Turn a frame into 10 rows of '#'/'.' for easy assertions."""
    px = [hex_frame[i : i + 6] for i in range(0, len(hex_frame), 6)]
    return ["".join("." if p == "000000" else "#" for p in px[y * 12 : y * 12 + 12]) for y in range(10)]


def test_canvas_hex_length_and_order():
    c = Canvas()
    c.set(0, 0, (255, 0, 0))
    c.set(11, 9, (0, 0, 255))
    h = c.to_hex()
    assert len(h) == 120 * 6
    assert h[:6] == "FF0000"
    assert h[-6:] == "0000FF"


@pytest.fixture
async def frames(hass: HomeAssistant):
    sent: list[str] = []

    async def fake_frame(call: ServiceCall) -> None:
        sent.append(call.data["pixels"])

    hass.services.async_register("esphome", FRAME_SERVICE, fake_frame)
    return sent


@pytest.fixture
async def setup_display(hass: HomeAssistant, frames):
    entry = MockConfigEntry(domain=DOMAIN, data={"frame_service": FRAME_SERVICE}, title="Led Display")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_show_text_top_line(hass: HomeAssistant, setup_display, frames):
    await hass.services.async_call(
        DOMAIN, "show_text", {"line": "top", "left": "C", "separator": ":", "right": "5", "color": "green"}, blocking=True
    )
    rows = render(frames[-1])
    assert rows[:5] == [
        ".##.....###.",
        "#....#..#...",
        "#.......###.",
        "#....#....#.",
        ".##.....###.",
    ]
    assert all(r == "." * 12 for r in rows[5:])
    # green
    assert frames[-1][:6] == "000000" and frames[-1][6:12] == "008000"


async def test_lines_are_independent_and_colours_override(hass: HomeAssistant, setup_display, frames):
    await hass.services.async_call(DOMAIN, "show_text", {"line": "top", "left": "C", "right": "5"}, blocking=True)
    await hass.services.async_call(
        DOMAIN,
        "show_text",
        {"line": "bottom", "left": "L", "right": "+", "right_color": "#FF8000"},
        blocking=True,
    )
    rows = render(frames[-1])
    assert rows[0] == ".##.....###."  # top line kept
    assert rows[5] == "#..........."
    assert rows[7] == "#.......###."
    px = frames[-1]
    # right '+' centre pixel at (9, 7) is orange, 'L' at (0, 5) is white
    assert px[(7 * 12 + 9) * 6 : (7 * 12 + 9) * 6 + 6] == "FF8000"
    assert px[(5 * 12 + 0) * 6 : (5 * 12 + 0) * 6 + 6] == "FFFFFF"


async def test_slot_rejects_two_characters(hass: HomeAssistant, setup_display):
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(DOMAIN, "show_text", {"line": "top", "right": "12"}, blocking=True)


async def test_number_slot_from_template_value(hass: HomeAssistant, setup_display, frames):
    await hass.services.async_call(DOMAIN, "show_text", {"line": "top", "right": 7}, blocking=True)
    assert render(frames[-1])[0] == "........###."


async def test_clear(hass: HomeAssistant, setup_display, frames):
    await hass.services.async_call(DOMAIN, "show_text", {"line": "top", "left": "#"}, blocking=True)
    await hass.services.async_call(DOMAIN, "show_text", {"line": "bottom", "left": "#"}, blocking=True)
    await hass.services.async_call(DOMAIN, "clear", {"line": "top"}, blocking=True)
    rows = render(frames[-1])
    assert rows[0] == "." * 12 and rows[5] == "###........."
    await hass.services.async_call(DOMAIN, "clear", {}, blocking=True)
    assert all(r == "." * 12 for r in render(frames[-1]))


async def test_no_display_errors(hass: HomeAssistant, frames):
    assert await async_setup_component(hass, DOMAIN, {})
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(DOMAIN, "show_text", {"line": "top", "left": "A"}, blocking=True)


async def test_config_flow(hass: HomeAssistant, frames):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result["type"] == "form"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"frame_service": FRAME_SERVICE})
    assert result["type"] == "create_entry"
    assert result["title"] == "Led Display"
    assert result["data"] == {"frame_service": FRAME_SERVICE}


async def test_config_flow_no_panels(hass: HomeAssistant):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    assert result["type"] == "abort"
    assert result["reason"] == "no_panels"


async def test_bus_channel_script(hass: HomeAssistant, setup_display, frames):
    """Run the bus channel script from the repo against fake sensors."""
    from pathlib import Path

    from homeassistant.util.yaml import parse_yaml

    script = parse_yaml((Path(__file__).parents[1] / "homeassistant/channels/bus_line_21.yaml").read_text())
    hass.states.async_set("sensor.bus_line_21_next_to_centraal", "4")
    hass.states.async_set("sensor.bus_line_21_to_lohmanstraat", "none")
    assert await async_setup_component(hass, "script", {"script": {"smart_led_bus_line_21": script}})
    await hass.services.async_call("script", "smart_led_bus_line_21", blocking=True)
    await hass.async_block_till_done()
    rows = render(frames[-1])
    assert rows[0] == ".##.....#.#."  # C : 4
    assert rows[7] == "#.......###."  # L : -
    px = frames[-1]
    assert px[(0 * 12 + 8) * 6 : (0 * 12 + 8) * 6 + 6] == "FFA500"  # 4 min -> orange
    hass.states.async_set("sensor.bus_line_21_next_to_centraal", "14")
    await hass.services.async_call("script", "smart_led_bus_line_21", blocking=True)
    await hass.async_block_till_done()
    assert render(frames[-1])[2] == "#.......###."  # '+' middle row
