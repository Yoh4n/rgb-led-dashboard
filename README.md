# RGB LED Dashboard

A CircuitPython weather dashboard for a 64×32 RGB LED matrix driven by an Adafruit MatrixPortal S3. It pulls current conditions and today's forecast from OpenWeatherMap and shows them alongside a weather icon.

## What it shows

- Day of the week
- "Feels like" temperature, today's high, and today's low (°F)
- Chance of rain (or snow) for the coming hour
- Wind speed (MPH)
- An icon for the current conditions

The display refreshes every `REFRESH_RATE` seconds. If a request fails, it shows an error screen and retries after `ERROR_WAIT` seconds.

## Hardware

- [Adafruit MatrixPortal S3](https://www.adafruit.com/product/5778)
- 64×32 RGB LED matrix (HUB75)
- USB-C power supply

Tested on CircuitPython 10.0.3.

## Setup

1. Install [CircuitPython](https://circuitpython.org/board/adafruit_matrixportal_s3/) on the MatrixPortal S3.
2. Copy everything in this repo to the `CIRCUITPY` drive. The required libraries are already in `lib/`.
3. Copy `settings_example.toml` to `settings.toml` on the drive and fill it in:

   | Key | Description |
   | --- | --- |
   | `CIRCUITPY_WIFI_SSID` | WiFi network name |
   | `CIRCUITPY_WIFI_PASSWORD` | WiFi password |
   | `OPEN_WEATHER_URL` | OpenWeatherMap One Call endpoint (the default is fine) |
   | `OPEN_WEATHER_MAP_API_KEY` | Your [OpenWeatherMap](https://openweathermap.org/api) API key |
   | `REFRESH_RATE` | Seconds between weather updates |
   | `ERROR_WAIT` | Seconds to wait before retrying after an error |
   | `DEFAULT_ZIP_CODE` | ZIP or postal code for the forecast location |
   | `DEFAULT_COUNTRY` | Two-letter country code, e.g. `US` |
   | `DEFAULT_APP` | Reserved for selecting an app (currently only weather) |

   `settings.toml` is git-ignored, so your credentials stay local.

4. The board restarts and the dashboard appears once it connects to WiFi.

> **Note:** The One Call 3.0 API requires the "One Call by Call" subscription on your OpenWeatherMap account, which has a free daily allowance.

## Time zone

The clock is set over NTP with a fixed UTC offset in `code.py`:

```python
ntp = adafruit_ntp.NTP(pool, tz_offset=-6, cache_seconds=3600)
```

Change `tz_offset` for your time zone. The value is fixed, so it does not adjust for daylight saving time.

## Project layout

```
code.py               Entry point: WiFi, clock, matrix setup, main loop
helpers.py            Date and string helpers
apps/weather.py       Weather app: fetches data and draws the screen
fonts/                Bitmap fonts (.bdf)
img/weather/          Weather condition icons, named by OpenWeatherMap icon code
lib/                  CircuitPython libraries
sd/                   SD card mount point
settings_example.toml Template for settings.toml
```
