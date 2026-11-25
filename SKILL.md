---
name: smart-led
description: Create, change and test smart-led channels. Each channel is a virtual LED screen controlled by Home Assistant and rendered as an effect in the ESP32 LED config. Use when adding a channel, mapping a channel to an effect, or editing LED effect parameters.
---

# smart-led

smart-led turns one physical LED panel into several virtual screens. Home Assistant addresses a channel. The ESP32 renders the channel's effect.

## Terms

- **Channel**: a named virtual screen exposed to Home Assistant.
- **Effect**: the rendering routine for a channel, defined in the LED section of the ESP32 config.

## Adding a channel

1. Give the channel a short lowercase name, for example `bus-countdown`.
2. Pick an existing effect from the ESP32 LED section, or add a new one there.
3. Record the channel in `channels/<name>.yaml` with its effect and parameters.
4. Expose the channel to Home Assistant and test it from the Home Assistant UI before relying on it in automations.

## Rules

- Effects live in the ESP32 config. Do not duplicate effect logic in Home Assistant.
- Channel names are the contract with Home Assistant, so do not rename a channel without updating its automations.
- Keep effect parameters explicit in the channel file rather than hard-coded in the effect.

## Open items

- Panel size and pixel layout (to be confirmed from the bus-arrival project).
- Effect list for the ESP32 LED section.
- Home Assistant entity naming convention for channels.
