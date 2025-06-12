from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up NED Energy from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload NED Energy config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)



