import time


def parse_datetime(dt_str):
    date_part, time_part = dt_str.split("T")
    year, month, day = map(int, date_part.split("-"))

    time_fields = time_part.split(":")
    hour = int(time_fields[0])
    minute = int(time_fields[1])
    second_float = float(time_fields[2])
    second = int(second_float)

    return time.struct_time((year, month, day, hour, minute, second, -1, -1, -1))


def get_dayofweek(day_int):
    weekdays = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    return weekdays[day_int]


def time_difference(dt_a, dt_b):
    try:
        time1 = time.mktime(parse_datetime(dt_a))
        time2 = time.mktime(parse_datetime(dt_b))
        diff_seconds = abs(time2 - time1)
        return diff_seconds / 60
    except Exception as e:
        print(f"Error calculating time difference: {e}")
        return 0


def pad_string(input_string):
    length = len(input_string)
    if length < 12:
        return input_string
    padding = " " * length
    return input_string + padding


def before_decimal(input_string):
    if "." in input_string:
        return input_string.split(".")[0]
    return input_string
