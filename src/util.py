def kelvin_to_celsius(kelvin: int | float):
    """Convert Kelvin to Celsius."""
    return round(kelvin - 273.15)

def kelvin_to_fahrenheit(kelvin: int | float):
    """Convert Kelvin to Fahrenheit."""
    celsius = kelvin_to_celsius(kelvin)
    return round((celsius * 9/5) + 32)

def fahrenheit_to_kelvin(fahrenheit: int | float):
    """Convert Fahrenheit to Kelvin."""
    kelvin = (fahrenheit - 32) * 5/9 + 273.15
    return kelvin

def celsius_to_kelvin(celsius: int | float):
    """Convert Kelvin to Fahrenheit."""
    kelvin = celsius + 273.15
    return kelvin
