import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SENSOR_TYPE
from homeassistant.core import HomeAssistant
from .const import DOMAIN, UPDATE_LISTENER

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Template sensor from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Update listener for config option changes
    update_listener = entry.add_update_listener(_async_update_listener)
    hass.data[DOMAIN][entry.entry_id] = {
        UPDATE_LISTENER: update_listener,
    }

    sensor_platform = entry.data[CONF_SENSOR_TYPE]
    await hass.config_entries.async_forward_entry_setups(entry, [sensor_platform])
    return True

async def _async_update_listener(hass: HomeAssistant, config_entry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry"""

    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, entry.data[CONF_SENSOR_TYPE])
    hass.data[DOMAIN][entry.entry_id][UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok