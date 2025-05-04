import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.entity import EntityCategory
from datetime import timedelta
from .ned_api_client import async_get_energy_mix

_LOGGER = logging.getLogger(__name__)
DOMAIN = "ned_energy"
SCAN_INTERVAL = timedelta(minutes=15)

SENSOR_TYPES = {
    "solar": {
        "name": "NED Solar Percentage",
        "unit": "%",
        "icon": "mdi:weather-sunny"
    },
    "wind": {
        "name": "NED Wind Percentage",
        "unit": "%",
        "icon": "mdi:weather-windy"
    },
    "green": {
        "name": "NED Green Energy Percentage",
        "unit": "%",
        "icon": "mdi:leaf"
    }
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    api_key = config_entry.data[CONF_API_KEY]

    async def async_update_data():
        data = await async_get_energy_mix(api_key=api_key)
        if data and len(data) > 0:
            return data
        return None

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="NED Energy Data",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    entities = [
        NedEnergySensor(coordinator, "solar"),
        NedEnergySensor(coordinator, "wind"),
        NedEnergySensor(coordinator, "green")
    ]
    async_add_entities(entities, True)

class NedEnergySensor(CoordinatorEntity):
    def __init__(self, coordinator, sensor_type):
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = SENSOR_TYPES[sensor_type]["name"]
        self._attr_icon = SENSOR_TYPES[sensor_type]["icon"]
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type]["unit"]
        self._attr_unique_id = f"ned_energy_{sensor_type}"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None
        latest = data[-1]
        if self._sensor_type == "solar":
            return latest.get("solar_percentage")
        elif self._sensor_type == "wind":
            return latest.get("wind_percentage")
        elif self._sensor_type == "green":
            return latest.get("green_percentage")
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or []
        return {
            "today_data": data
        }
