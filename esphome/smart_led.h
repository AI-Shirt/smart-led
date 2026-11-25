#pragma once
// smart-led helpers: treat the LED strip as a small computer display.
//
// Logical coordinates: (0,0) is the top-left pixel, x grows to the right, y grows down.
// Physical layout: one vertical strip per column, column 0 on the left,
// LED 0 at the top of column 0. With serpentine wiring the odd columns run
// bottom to top; without it every column runs top to bottom.

#include <cstdint>
#include "esphome/core/color.h"
#include "esphome/components/light/addressable_light.h"
#include "esphome/components/light/esp_hsv_color.h"

namespace smart_led {

// Strip index for pixel (x, y), or -1 when the pixel is off the display.
inline int xy(int x, int y, int width, int height, bool serpentine) {
  if (x < 0 || y < 0 || x >= width || y >= height)
    return -1;
  int row = (serpentine && (x & 1)) ? (height - 1 - y) : y;
  return x * height + row;
}

inline void set(esphome::light::AddressableLight &it, int x, int y, int width, int height, bool serpentine,
                const esphome::Color &c) {
  int i = xy(x, y, width, height, serpentine);
  if (i >= 0 && i < it.size())
    it[i] = c;
}

// hue, saturation and value all 0..255
inline esphome::Color hsv(uint8_t h, uint8_t s, uint8_t v) {
  return esphome::light::ESPHSVColor(h, s, v).to_rgb();
}

}  // namespace smart_led
