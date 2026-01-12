"""Device data model."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from .utils import get_product_by_type_version

from . import utils
from .dto import EnergyConsumptionData
from .model import RointeProduct, ScheduleMode


class RointeDevice:
    """Represent a Rointe device from the API."""

    id: str
    name: str
    serialnumber: str
    type: str

    # This represents the model of a particular product. Not the FW version.
    product_version: str

    firmware_version: Optional[str]
    latest_firmware_version: Optional[str]

    nominal_power: int
    nominal_effective_power: int
    power: bool

    # Describes the preset: ICE, ECO, Comfort, None
    preset: str
    mode: str

    temp: float
    temp_calc: float
    temp_probe: float

    # preset temperatures
    comfort_temp: float
    eco_temp: float
    ice_temp: float

    # User mode
    um_max_temp: float
    um_min_temp: float
    user_mode: bool
    ice_mode: bool

    # Schedule
    schedule: list[str]
    schedule_day: int
    schedule_hour: int

    energy_data: EnergyConsumptionData

    last_sync_datetime_app: datetime
    last_sync_datetime_device: datetime

    hass_available: bool

    def __init__(
        self,
        device_id: str,
        device_info: dict,
        energy_data: EnergyConsumptionData,
        latest_fw: str | None,
    ) -> None:
        """Initialize the device from the rointe's json blob."""
        self.id = device_id
        self.type = device_info["data"]["type"]
        self.product_version = str.lower(device_info["data"]["product_version"])
        self.serialnumber = device_info["serialnumber"]
        self.update_data(device_info, energy_data, latest_fw)

    def update_data(
        self,
        device_info: dict,
        energy_data: EnergyConsumptionData,
        latest_fw: str | None,
    ) -> None:
        """Update the device data from a Json object."""

        data = device_info["data"]
        firmware_data = device_info.get("firmware")

        self.name = data.get("name", "")
        self.nominal_power = int(data.get("nominal_power", 0))
        self.nominal_effective_power = int(
            data.get("nominal_effective_power", self.nominal_power)
        )
        power_val = data.get("power", False)
        power_int: int | None
        try:
            power_int = int(power_val)
        except (TypeError, ValueError):
            power_int = None
        status = data.get("status", "none")
        if status == "off":
            self.power = False
        elif power_int is not None:
            # Nexa uses 1=standby/off, 2=on/heating.
            self.power = power_int == 2
        else:
            self.power = bool(power_val)
        self.preset = status
        mode_val = data.get("mode", "manual")
        if mode_val in (0, "0"):
            self.mode = "manual"
        elif mode_val in (1, "1"):
            self.mode = "auto"
        else:
            self.mode = mode_val

        self.temp = float(data.get("temp", 0))
        self.temp_calc = float(data.get("temp_calc", self.temp))
        self.temp_probe = float(data.get("temp_probe", self.temp))

        self.comfort_temp = float(data.get("comfort", self.temp))
        self.eco_temp = float(data.get("eco", self.temp))
        self.ice_temp = float(data.get("ice", self.temp))

        # User mode settings are only valid for V2 radiators.
        if self.product_version == "v2":
            self.um_max_temp = float(data.get("um_max_temp", 0))
            self.um_min_temp = float(data.get("um_min_temp", 0))
            self.user_mode = bool(data.get("user_mode", False))
        else:
            self.um_max_temp = 0
            self.um_min_temp = 0
            self.user_mode = False

        self.ice_mode = bool(data.get("ice_mode", False))
        self.schedule = data.get("schedule", [])
        self.schedule_day = data.get("schedule_day", 0)
        self.schedule_hour = data.get("schedule_hour", 0)

        self.energy_data = energy_data

        if data.get("last_sync_datetime_app"):
            self.last_sync_datetime_app = datetime.fromtimestamp(
                int(data["last_sync_datetime_app"]) / 1000.0
            )
        else:
            self.last_sync_datetime_app = datetime.now()

        if data.get("last_sync_datetime_device"):
            self.last_sync_datetime_device = datetime.fromtimestamp(
                int(data["last_sync_datetime_device"]) / 1000.0
            )
        else:
            self.last_sync_datetime_device = datetime.now()

        if firmware_data:
            self.firmware_version = firmware_data.get("firmware_version_device")
        else:
            self.firmware_version = None

        self.latest_firmware_version = latest_fw
        self.hass_available = True

    def get_current_schedule_mode(self) -> ScheduleMode:
        """Return the current schedule mode for the device.

        Returns C for Comfort, E for Eco, O for no-schedule
        """
        day_time = utils.now()
        day_of_week = day_time.weekday()  # 0 is Monday
        hour_index = day_time.hour

        current_mode = self.schedule[day_of_week][hour_index]

        if current_mode == "C":
            return ScheduleMode.COMFORT
        elif current_mode == "E":
            return ScheduleMode.ECO
        else:
            return ScheduleMode.NONE

    def user_mode_supported(self) -> bool:
        """Return True if this device supports user mode."""
        return self.product_version == "v2"

    @property
    def rointe_product(self) -> RointeProduct | None:
        """Return the product name."""
        return get_product_by_type_version(self.type, self.product_version)
