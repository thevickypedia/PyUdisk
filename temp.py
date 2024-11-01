from src.main import disk_info, monitor
from src import util


if __name__ == "__main__":
    monitor()
    # for disk in disk_info():
    #     print(disk.id)
    #     print(util.kelvin_to_celsius(disk.Attributes.SmartTemperature))
    #     print(util.kelvin_to_fahrenheit(disk.Attributes.SmartTemperature))
    #     print(disk.Attributes.SmartNumBadSectors)
