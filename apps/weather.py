import os
import math
import displayio
import time
import adafruit_imageload
from helpers import get_dayofweek
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

OPEN_WEATHER_URL = os.getenv("OPEN_WEATHER_URL")
OPEN_WEATHER_MAP_API_KEY = os.getenv("OPEN_WEATHER_MAP_API_KEY")
DEFAULT_ZIP_CODE = os.getenv("DEFAULT_ZIP_CODE")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY")
REFRESH_RATE = int(os.getenv("REFRESH_RATE", 1800))
ERROR_WAIT = int(os.getenv("ERROR_WAIT", 900))

COL_A_ANCHOR = [2, 9]
COL_B_ANCHOR = [17, 9]
COL_C_ANCHOR = [22, 9]

PADDING = 2


class WeatherApp:
    def __init__(self, display, requests):
        self.zip_code = DEFAULT_ZIP_CODE
        self.country_code = DEFAULT_COUNTRY.upper()
        self.requests = requests
        self.location = self.get_location()
        self.display = display
        self.last_update_time = time.monotonic()
        self.font = bitmap_font.load_font("../fonts/5x8.bdf", displayio.Bitmap)
        self.font_small = bitmap_font.load_font("../fonts/04b_24.bdf", displayio.Bitmap)
        self.is_error = False

        self.root_group = displayio.Group()
        self.img_group = displayio.Group()
        self.root_group.append(self.img_group)
        self.display.root_group = self.root_group

    def _create_label(self, text, x, y, font=None, color=(255, 255, 255)):
        return label.Label(
            font or self.font,
            text=text,
            color=color,
            anchor_point=(0, 0),
            anchored_position=(x, y),
        )

    def get_location(self):
        url = f"http://api.openweathermap.org/geo/1.0/zip?zip={self.zip_code},{self.country_code}&limit=1&appid={OPEN_WEATHER_MAP_API_KEY}"
        response = self.requests.get(url)
        return response.json() if response.status_code == 200 else None

    def fetch_weather_data(self):
        if not self.location:
            self.location = self.get_location()
        location = self.location
        if not location:
            return None

        lat, lon = location["lat"], location["lon"]
        url = f"{OPEN_WEATHER_URL}?lat={lat}&lon={lon}&units=imperial&appid={OPEN_WEATHER_MAP_API_KEY}"
        response = self.requests.get(url)
        if response.status_code != 200:
            return None

        data = response.json()
        hourly = data["hourly"][0]
        daily = data["daily"][0]
        current = data["current"]
        weather = hourly["weather"][0]

        return {
            "pop": f"{math.ceil(hourly['pop'] * 100)}%",
            "daily_hi": str(math.ceil(daily["temp"]["max"])),
            "daily_lo": str(math.floor(daily["temp"]["min"])),
            "feels_like": str(math.ceil(current["feels_like"])),
            "humidity": str(math.ceil(current["humidity"])),
            "wind_speed": f"{math.ceil(hourly['wind_speed'])}MPH",
            "condition_id": weather["icon"],
            "snow": weather["main"] == "Snow",
        }

    def get_weather_icon(self, condition):
        image, palette = adafruit_imageload.load(f"../img/weather/{condition}.png")
        return displayio.TileGrid(image, pixel_shader=palette)

    def update_labels(self, data):
        self.pop.text = "SNOW" if data["snow"] else "RAIN"
        self.city.text = get_dayofweek(time.localtime().tm_wday).upper()

        self.feels_like_int.text = data["feels_like"]
        self.temp_hi_int.text = data["daily_hi"]
        self.temp_lo_int.text = data["daily_lo"]
        self.wind_speed_int.text = data["wind_speed"]
        self.pop_int.text = data["pop"]

        # Reposition the temp labels based on digit count
        self._reposition_temps()

        self.img_group.pop()
        self.img_group.append(self.get_weather_icon(data["condition_id"]))

    def draw_screen(self):
        data = self.fetch_weather_data()
        if not data:
            self.draw_error()
            return

        icon = self.get_weather_icon(data["condition_id"])
        pop_text = "SNOW" if data["snow"] else "RAIN"

        self.city = self._create_label(
            get_dayofweek(time.localtime().tm_wday).upper(), 2, 1, color=(255, 255, 255)
        )

        self.feels_like_int = self._create_label(
            data["feels_like"],
            COL_A_ANCHOR[0],
            COL_A_ANCHOR[1],
            color=(230, 175, 25),
        )

        # --- HIGH TEMP ---
        hi_x = (
            self.feels_like_int.anchored_position[0]
            + self._label_width(self.feels_like_int)
            + PADDING
        )

        self.temp_hi_int = self._create_label(
            data["daily_hi"],
            hi_x,
            COL_B_ANCHOR[1],
            color=(230, 25, 65),
        )

        # --- LOW TEMP ---
        lo_x = hi_x + self._label_width(self.temp_hi_int) + PADDING

        self.temp_lo_int = self._create_label(
            data["daily_lo"],
            lo_x,
            COL_C_ANCHOR[1],
            color=(25, 140, 225),
        )

        self.pop = self._create_label(pop_text, 2, 17, color=(255, 255, 255))
        self.pop_int = self._create_label(data["pop"], 24, 17, color=(255, 255, 255))

        self.wind_speed = self._create_label("WIND", 2, 25, color=(255, 255, 255))
        self.wind_speed_int = self._create_label(
            data["wind_speed"], 24, 25, color=(255, 255, 255)
        )

        self.img_group.append(icon)
        self.img_group.x = 42
        self.img_group.y = 0

        for element in [
            self.city,
            self.temp_hi_int,
            self.temp_lo_int,
            self.feels_like_int,
            self.wind_speed,
            self.wind_speed_int,
            self.pop,
            self.pop_int,
        ]:
            self.root_group.append(element)

    def draw_error(self):
        # Clear root_group and img_group
        self.is_error = True
        while len(self.root_group) > 0:
            self.root_group.pop()
        while len(self.img_group) > 0:
            self.img_group.pop()

        # Reset group hierarchy
        self.root_group.append(self.img_group)

        # Create error label
        self.city = label.Label(
            font=self.font_small,
            text="404 not found...",
            anchor_point=(0.0, 0.0),
            anchored_position=(2, 1),
        )

        # Position error icon
        self.img_group.x = 0
        self.img_group.y = 0
        self.img_group.append(self.get_weather_icon("err"))

        # Append the error label to root_group
        self.root_group.append(self.city)

    def update_weather(self):
        data = self.fetch_weather_data()
        if not data:
            return False
        self.update_labels(data)
        self.is_error = False
        return True

    def render(self):
        now = time.monotonic()
        if now >= self.last_update_time + REFRESH_RATE:
            if not self.update_weather():
                self.last_update_time = now + ERROR_WAIT
                if not self.is_error:
                    self.draw_error()
            else:
                self.last_update_time = now
        else:
            time_remaining = self.last_update_time + REFRESH_RATE - now
            time.sleep(min(time_remaining, 60))

    def _label_width(self, label):
        # bounding_box = (x, y, width, height)
        return label.bounding_box[2]

    def _reposition_temps(self):
        # Reposition high temp
        hi_x = (
            self.feels_like_int.anchored_position[0]
            + self._label_width(self.feels_like_int)
            + PADDING
        )
        
        self.temp_hi_int.anchored_position = (hi_x, COL_B_ANCHOR[1])

        # Reposition low temp
        lo_x = hi_x + self._label_width(self.temp_hi_int) + PADDING
        self.temp_lo_int.anchored_position = (lo_x, COL_C_ANCHOR[1])