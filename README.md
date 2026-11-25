# smart-led

A Claude skill project for **smart-led**, a product that turns the LED panel built for the bus-arrival display into a set of virtual LED screens.

Home Assistant controls the panel. Each **channel** is a virtual screen, and each channel is an **effect** in the LED section of the ESP32 configuration.

## Concept

- **Panel**: physical LED panel driven by an ESP32.
- **Channel**: a virtual screen that Home Assistant can address by name.
- **Effect**: the rendering behaviour for a channel. The ESP32 config defines the effect list in its LED section, and each channel maps to one effect.

## Status

Scaffold only. Channel definitions and the ESP32 LED section are still to be written.

## Layout

- `SKILL.md`: the Claude skill that knows how to add, change and test channels.
- `channels/`: one file per channel (name, effect, parameters).
- `esphome/`: ESP32 LED section snippets for the effects.

## Decisions

- **Firmware:** ESPHome-based. Each channel is an effect in the ESP32 LED section.
- **Scope of first release:** effects only. Live Home Assistant data channels (bus countdowns, sensors) come later.
- **Audience:** built to be usable by others. Needs a parts list, a pre-built firmware binary with a browser flasher, and simple setup.
- **Distribution:** HACS-ready custom repository (`custom_components/smart_led/`, `hacs.json`, tagged releases).

## Build order

1. ESPHome firmware and effects for the 12x10 panel.
2. Home Assistant integration that creates one entity per channel.
3. Hardware parts list, wiring diagram, flasher and setup docs.
