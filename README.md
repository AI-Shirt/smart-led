# smart-led

A Claude skill project for **smart-led**, a product that turns the LED panel built for the bus-arrival display into a set of virtual LED screens.

Home Assistant controls the panel. Each **channel** is a virtual screen, and each channel is an **effect** in the LED section of the ESP32 configuration.

## Concept

- **Panel**: physical LED panel driven by an ESP32.
- **Channel**: a virtual screen that Home Assistant can address by name.
- **Effect**: the rendering behaviour for a channel. The ESP32 config defines the effect list in its LED section, and each channel maps to one effect.

## Status

Working: ESPHome firmware with a virtual-display frame action, the Smart LED integration (v0.1.0) and a bus line 21 channel.

## Smart LED integration

Install `custom_components/smart_led` into Home Assistant, restart, then add **Smart LED** under Devices & services and pick your panel's `show_frame` action.

Actions:

- `smart_led.show_text`: draws one line (`top` or `bottom`) as three one-character slots, `left`, `separator` and `right`, with a `color` and optional per-slot colours (`left_color`, `separator_color`, `right_color`). Colours can be names, hex (`#FF8000`) or `[r, g, b]`.
- `smart_led.clear`: blanks `top`, `bottom` or `all`.

```yaml
action: smart_led.show_text
data:
  line: top
  left: "C"
  separator: ":"
  right: "5"
  color: white
  right_color: green
```

## Layout

- `SKILL.md`: the Claude skill that knows how to add, change and test channels.
- `custom_components/smart_led/`: the Home Assistant integration.
- `homeassistant/channels/`: one script per channel.
- `tests/`: integration tests (`pytest`).
- `esphome/smart-led.yaml`: ESPHome firmware config. Each channel is an effect in the light section.
- `esphome/smart_led.h`: helpers that map display coordinates ((0,0) top-left) to strip LEDs.

## Decisions

- **Firmware:** ESPHome-based. Each channel is an effect in the ESP32 LED section.
- **Scope of first release:** effects only. Live Home Assistant data channels (bus countdowns, sensors) come later.
- **Audience:** built to be usable by others. Needs a parts list, a pre-built firmware binary with a browser flasher, and simple setup.
- **Distribution:** HACS-ready custom repository (`custom_components/smart_led/`, `hacs.json`, tagged releases).

## Build order

1. ESPHome firmware and effects for the 12x10 panel.
2. Home Assistant integration that creates one entity per channel.
3. Hardware parts list, wiring diagram, flasher and setup docs.
