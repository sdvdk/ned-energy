import logging
from homeassistant.helpers.entity import Entity
from .ned_api_client import get_energy_mix

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    api_key = config.get("api_key")
    if not api_key:
        _LOGGER.error("No API key provided for NED Energy sensor")
        return

    # Fetch the data (currently synchronously, should be async in the future)
    data = get_energy_mix(days=1)
    if data and len(data) > 0:
        latest = data[-1]
        async_add_entities([
            NedEnergySensor(latest)
        ], True)
    else:
        _LOGGER.error("No data received from NED API")

class NedEnergySensor(Entity):
    def __init__(self, data):
        self._state = data["green_percentage"]
        self._attributes = data

    @property
    def name(self):
        return "NED Green Energy Percentage"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes
