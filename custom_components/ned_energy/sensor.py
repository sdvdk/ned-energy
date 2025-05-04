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
    "solar_volume": {"name": "NED Solar Volume", "unit": "kWh", "icon": "mdi:weather-sunny", "attr": "solar_volume"},
    "solar_percentage": {"name": "NED Solar Percentage", "unit": "%", "icon": "mdi:weather-sunny", "attr": "solar_percentage"},
    "wind_volume": {"name": "NED Wind Volume", "unit": "kWh", "icon": "mdi:weather-windy", "attr": "wind_volume"},
    "wind_percentage": {"name": "NED Wind Percentage", "unit": "%", "icon": "mdi:weather-windy", "attr": "wind_percentage"},
    "wind_offshore_volume": {"name": "NED Wind Offshore Volume", "unit": "kWh", "icon": "mdi:weather-windy", "attr": "wind_offshore_volume"},
    "wind_offshore_percentage": {"name": "NED Wind Offshore Percentage", "unit": "%", "icon": "mdi:weather-windy", "attr": "wind_offshore_percentage"},
    "green_percentage": {"name": "NED Green Energy Percentage", "unit": "%", "icon": "mdi:leaf", "attr": "green_percentage"},
    "total_volume": {"name": "NED Total Volume", "unit": "kWh", "icon": "mdi:flash", "attr": "total_volume"},
    "coal_volume": {"name": "NED Coal Volume", "unit": "kWh", "icon": "mdi:factory", "attr": "coal_volume"},
    "coal_percentage": {"name": "NED Coal Percentage", "unit": "%", "icon": "mdi:factory", "attr": "coal_percentage"},
    "gas_volume": {"name": "NED Gas Volume", "unit": "kWh", "icon": "mdi:fire", "attr": "gas_volume"},
    "gas_percentage": {"name": "NED Gas Percentage", "unit": "%", "icon": "mdi:fire", "attr": "gas_percentage"},
    "nuclear_volume": {"name": "NED Nuclear Volume", "unit": "kWh", "icon": "mdi:radioactive", "attr": "nuclear_volume"},
    "nuclear_percentage": {"name": "NED Nuclear Percentage", "unit": "%", "icon": "mdi:radioactive", "attr": "nuclear_percentage"},
    "biomass_volume": {"name": "NED Biomass Volume", "unit": "kWh", "icon": "mdi:leaf", "attr": "biomass_volume"},
    "biomass_percentage": {"name": "NED Biomass Percentage", "unit": "%", "icon": "mdi:leaf", "attr": "biomass_percentage"},
    "hydro_volume": {"name": "NED Hydro Volume", "unit": "kWh", "icon": "mdi:waves", "attr": "hydro_volume"},
    "hydro_percentage": {"name": "NED Hydro Percentage", "unit": "%", "icon": "mdi:waves", "attr": "hydro_percentage"},
    "other_volume": {"name": "NED Other Volume", "unit": "kWh", "icon": "mdi:help-circle", "attr": "other_volume"},
    "other_percentage": {"name": "NED Other Percentage", "unit": "%", "icon": "mdi:help-circle", "attr": "other_percentage"},
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
        NedEnergySensor(coordinator, key)
        for key in SENSOR_TYPES.keys()
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
        attr = SENSOR_TYPES[self._sensor_type]["attr"]
        # For source volumes, get from latest or 0 if missing
        if attr in latest:
            return latest.get(attr)
        # For other sources (coal, gas, etc.), get from today_data if present
        if "today_data" in latest:
            return latest["today_data"].get(attr, 0)
        return 0

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or []
        attr = SENSOR_TYPES[self._sensor_type]["attr"]
        filtered_data = []
        is_percentage = self._sensor_type.endswith("_percentage")
        for entry in data:
            filtered_entry = {"timestamp": entry.get("timestamp")}
            # Always include the value, default to 0 if missing
            filtered_entry[attr] = entry.get(attr, 0)
            # For percentage sensors, also include the corresponding volume, default to 0
            if is_percentage:
                volume_attr = attr.replace("_percentage", "_volume")
                filtered_entry[volume_attr] = entry.get(volume_attr, 0)
            filtered_data.append(filtered_entry)
        return {
            "today_data": filtered_data
        }
