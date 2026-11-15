import os
import board
import wifi
import rtc
import neopixel
import adafruit_connection_manager
import adafruit_requests
import adafruit_ntp
from adafruit_matrixportal.matrix import Matrix
from apps.weather import WeatherApp


pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

# Configure clock
ntp = adafruit_ntp.NTP(pool, tz_offset=-6, cache_seconds=3600)
rtc.RTC().datetime = ntp.datetime

matrix = Matrix(bit_depth=6, color_order="RGB")
display = matrix.display
display.auto_refresh = True


def connect_wifi():
    if not wifi.radio.connected:
        wifi.radio.connect(
            os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD")
        )
        print(f"Connected")
    else:
        pixel.fill((0, 0, 0))
        print("Connected")
        

if __name__ == "__main__":
    connect_wifi()
    app = WeatherApp(display, requests)
    app.draw_screen()

    while True:
        try:
            app.render()
        except Exception as e:
            print(f"Error in main loop: {e}")
