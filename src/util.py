def kelvin_to_celsius(kelvin):
    """Convert Kelvin to Celsius."""
    return round(kelvin - 273.15)

def kelvin_to_fahrenheit(kelvin):
    """Convert Kelvin to Fahrenheit."""
    celsius = kelvin_to_celsius(kelvin)
    return round((celsius * 9/5) + 32)
