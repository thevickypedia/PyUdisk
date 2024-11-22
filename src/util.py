import math


def kelvin_to_celsius(kelvin: int | float):
    """Convert Kelvin to Celsius."""
    return round(kelvin - 273.15)


def kelvin_to_fahrenheit(kelvin: int | float):
    """Convert Kelvin to Fahrenheit."""
    celsius = kelvin_to_celsius(kelvin)
    return round((celsius * 9 / 5) + 32)


def fahrenheit_to_kelvin(fahrenheit: int | float):
    """Convert Fahrenheit to Kelvin."""
    kelvin = (fahrenheit - 32) * 5 / 9 + 273.15
    return kelvin


def celsius_to_kelvin(celsius: int | float):
    """Convert Kelvin to Fahrenheit."""
    kelvin = celsius + 273.15
    return kelvin


def format_nos(input_: float) -> int | float:
    """Removes ``.0`` float values.

    Args:
        input_: Strings or integers with ``.0`` at the end.

    Returns:
        int | float:
        Int if found, else returns the received float value.
    """
    return int(input_) if isinstance(input_, float) and input_.is_integer() else input_


def size_converter(byte_size: int | float) -> str:
    """Gets the current memory consumed and converts it to human friendly format.

    Args:
        byte_size: Receives byte size as argument.

    Returns:
        str:
        Converted understandable size.
    """
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    index = int(math.floor(math.log(byte_size, 1024)))
    return f"{format_nos(round(byte_size / pow(1024, index), 2))} {size_name[index]}"
