from __future__ import annotations
import logging

# from homeassistant.components.sensor import NON_NUMERIC_DEVICE_CLASSES, SensorDeviceClass

from homeassistant.components.template.sensor import SensorTemplate
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.template import Template, slugify
from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_ICON,
    CONF_NAME,
    CONF_STATE,
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# from homeassistant.helpers.template_entity import TemplateEntity
# from homeassistant.util.enum import try_parse_enum


from .const import DEFAULT_ICON, TEXT_NONE

TEMPLATE_KEYS = [CONF_NAME, CONF_STATE, CONF_ICON]

NO_SLUGIFY_KEYS = [CONF_UNIT_OF_MEASUREMENT]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Add binary sensors for hikvision events states."""
    entity_cfg: dict = {}
    for key, value in entry.data.items():
        if key in TEMPLATE_KEYS and isinstance(value, str):
            entity_cfg[key] = Template(value)
        elif slugify(value) == TEXT_NONE:
            entity_cfg[key] = None
        else:
            if key in NO_SLUGIFY_KEYS:
                entity_cfg[key] = value
            else:
                entity_cfg[key] = slugify(value)

    # Set default icon if not in config or set by device class
    if not entity_cfg.get(CONF_ICON) and entity_cfg[CONF_DEVICE_CLASS] is None:
        entity_cfg[CONF_ICON] = Template(DEFAULT_ICON)

    # Set state template to blank if not valid for device_class
    # device_class = try_parse_enum(SensorDeviceClass, str(entity_cfg[CONF_DEVICE_CLASS]).upper())
    # if device_class in NON_NUMERIC_DEVICE_CLASSES:
    #    result = Template(entry.data[CONF_STATE]).async_render(variables={"this": TemplateEntity.DummyState()})

    entities = [SensorTemplate(hass, entity_cfg, f"custom_binary_sensor_{entry.data.get(CONF_NAME)}")]
    async_add_entities(entities)
