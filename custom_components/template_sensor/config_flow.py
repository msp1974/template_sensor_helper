"""
Config Flow for Template Sensor.
@msp1974
"""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.sensor import CONF_STATE_CLASS
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_ICON,
    CONF_NAME,
    CONF_SENSOR_TYPE,
    CONF_STATE,
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from homeassistant.helpers.template import slugify

from .const import DOMAIN, TEXT_NONE
from .helpers import get_device_class_list, get_device_class_state_classes, get_device_class_uoms, unslugify

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = [BINARY_SENSOR_DOMAIN, SENSOR_DOMAIN]


CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=""): cv.string,
        vol.Optional(CONF_SENSOR_TYPE, default=SENSOR_DOMAIN): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=SENSOR_TYPES, mode=selector.SelectSelectorMode.LIST, translation_key=CONF_SENSOR_TYPE
            ),
        ),
    }
)

TEMPLATE_SCHEMA = vol.Schema(
    {vol.Required(CONF_STATE, default=""): selector.TemplateSelector(selector.TemplateSelectorConfig())}
)


class TemplateSensorFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    sensor_type: str
    config: dict

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow handler."""
        return TemplateSensorOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle a Template Sensor config flow start."""
        errors = {}
        if user_input is not None:
            self.sensor_type = user_input[CONF_SENSOR_TYPE]
            self.config = user_input
            return await self.async_step_device_class()

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA, errors=errors, last_step=False)

    async def async_step_device_class(self, user_input=None):
        errors = {}
        if user_input is not None:
            self.config.update(user_input)
            if self.sensor_type == SENSOR_DOMAIN and slugify(user_input[CONF_DEVICE_CLASS]) != TEXT_NONE:
                return await self.async_step_state_class()
            return await self.async_step_template()

        schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE_CLASS, default=unslugify(TEXT_NONE)): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=get_device_class_list(self.config[CONF_SENSOR_TYPE]),
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    ),
                ),
            }
        )
        return self.async_show_form(step_id="device_class", data_schema=schema, errors=errors, last_step=False)

    async def async_step_state_class(self, user_input=None):
        errors = {}
        if user_input is not None:
            self.config.update(user_input)
            return await self.async_step_template()

        state_class_schema = vol.Schema(
            {
                vol.Optional(CONF_STATE_CLASS, default=unslugify(TEXT_NONE)): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=list(get_device_class_state_classes(self.config[CONF_DEVICE_CLASS])),
                        mode=selector.SelectSelectorMode.LIST,
                        translation_key=CONF_STATE_CLASS,
                    ),
                )
            }
        )
        return self.async_show_form(
            step_id="state_class", data_schema=state_class_schema, errors=errors, last_step=False
        )

    async def async_step_template(self, user_input=None):
        errors = {}
        if user_input is not None:
            self.config.update(user_input)

            await self.async_set_unique_id(f"{DOMAIN}-{self.config[CONF_NAME]}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"{DOMAIN}_{self.config[CONF_NAME]}",
                data=self.config,
            )

        # Add UOM to template schema based on device type selected if a sensor
        schema = TEMPLATE_SCHEMA

        if self.config.get(CONF_SENSOR_TYPE) == SENSOR_DOMAIN and slugify(self.config[CONF_DEVICE_CLASS]) != TEXT_NONE:
            units = get_device_class_uoms(self.config[CONF_DEVICE_CLASS])
            if len(units) > 1:
                schema = vol.Schema(
                    {
                        vol.Optional(CONF_UNIT_OF_MEASUREMENT): selector.SelectSelector(
                            selector.SelectSelectorConfig(
                                options=units,
                                mode=selector.SelectSelectorMode.DROPDOWN,
                                translation_key=CONF_UNIT_OF_MEASUREMENT,
                            )
                        ),
                    }
                ).extend(TEMPLATE_SCHEMA.schema)
            else:
                if units:
                    self.config[CONF_UNIT_OF_MEASUREMENT] = units[0]

        return self.async_show_form(step_id="template", data_schema=schema, errors=errors, last_step=True)


class TemplateSensorOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for template sensor."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = None

    async def async_step_init(self, user_input=None):
        menu_options = ["device_class", "value_template", "icon"]
        if self.config_entry.data[CONF_SENSOR_TYPE] == SENSOR_DOMAIN:
            # Check if units option should be added to menu
            units = get_device_class_uoms(self.config_entry.data[CONF_DEVICE_CLASS])
            if units and len(units) > 1:
                menu_options.append("unit_of_measurement")

            # Check if state class option should be added to menu
            state_classes = get_device_class_state_classes(self.config_entry.data[CONF_DEVICE_CLASS])
            if state_classes and len(state_classes) > 1:
                menu_options.append("state_class")

            return self.async_show_menu(step_id="init", menu_options=sorted(menu_options))
        return await self.async_step_value_template()

    async def async_step_device_class(self, user_input=None):
        if user_input is not None:
            # Set UOM if changing device_class
            if user_input[CONF_DEVICE_CLASS] != self.config_entry.data[CONF_DEVICE_CLASS]:
                units = get_device_class_uoms(user_input[CONF_DEVICE_CLASS])
                if units:
                    if len(units) > 1:
                        self.options = self.config_entry.data | user_input
                        return await self.async_step_unit_of_measurement()
                    else:
                        user_input[CONF_UNIT_OF_MEASUREMENT] = units[0]
                else:
                    user_input[CONF_UNIT_OF_MEASUREMENT] = None

            self.options = self.config_entry.data | user_input

            self.hass.config_entries.async_update_entry(self.config_entry, data=self.options)
            return self.async_create_entry(title="", data={})

        # Build options schema
        options_schema = {
            vol.Required(
                CONF_DEVICE_CLASS, default=self.config_entry.data[CONF_DEVICE_CLASS]
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=get_device_class_list(SENSOR_DOMAIN), mode=selector.SelectSelectorMode.DROPDOWN
                ),
            ),
        }

        return self.async_show_form(step_id="device_class", data_schema=vol.Schema(options_schema))

    async def async_step_state_class(self, user_input=None):
        """Handle selection of units after change of device class"""
        if user_input is not None:
            if self.options:
                self.options = self.options | user_input
            else:
                self.options = self.config_entry.data | user_input

            self.hass.config_entries.async_update_entry(self.config_entry, data=self.options)
            return self.async_create_entry(title="", data={})

        state_classes = get_device_class_state_classes(
            self.options.get(CONF_DEVICE_CLASS, self.config_entry.data[CONF_DEVICE_CLASS])
            if self.options
            else self.config_entry.data[CONF_DEVICE_CLASS]
        )
        options_schema = {
            vol.Optional(
                CONF_STATE_CLASS, default=self.config_entry.data.get(CONF_STATE_CLASS)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=state_classes,
                    mode=selector.SelectSelectorMode.LIST,
                    translation_key=CONF_UNIT_OF_MEASUREMENT,
                )
            ),
        }

        return self.async_show_form(step_id="state_class", data_schema=vol.Schema(options_schema))

    async def async_step_unit_of_measurement(self, user_input=None):
        """Handle selection of units after change of device class"""
        if user_input is not None:
            if self.options:
                self.options = self.options | user_input
            else:
                self.options = self.config_entry.data | user_input

            self.hass.config_entries.async_update_entry(self.config_entry, data=self.options)
            return self.async_create_entry(title="", data={})

        units = get_device_class_uoms(
            self.options.get(CONF_DEVICE_CLASS, self.config_entry.data[CONF_DEVICE_CLASS])
            if self.options
            else self.config_entry.data[CONF_DEVICE_CLASS]
        )
        options_schema = {
            vol.Optional(
                CONF_UNIT_OF_MEASUREMENT, default=self.config_entry.data.get(CONF_UNIT_OF_MEASUREMENT)
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=units, mode=selector.SelectSelectorMode.DROPDOWN, translation_key=CONF_UNIT_OF_MEASUREMENT
                )
            ),
        }

        return self.async_show_form(step_id="unit_of_measurement", data_schema=vol.Schema(options_schema))

    async def async_step_icon(self, user_input=None):
        """Handle selection of icon type"""
        if user_input is not None:
            self.options = self.config_entry.data | user_input

            self.hass.config_entries.async_update_entry(self.config_entry, data=self.options)
            return self.async_create_entry(title="", data={})

        options_schema = {
            vol.Optional(CONF_ICON, default=self.config_entry.data.get(CONF_ICON)): selector.TemplateSelector(
                selector.TemplateSelectorConfig()
            )
        }

        return self.async_show_form(step_id="icon", data_schema=vol.Schema(options_schema))

    async def async_step_value_template(self, user_input=None):
        """Handle change of value template"""
        if user_input is not None:
            self.options = self.config_entry.data | user_input

            self.hass.config_entries.async_update_entry(self.config_entry, data=self.options)
            return self.async_create_entry(title="", data={})

        options_schema = {
            vol.Required(CONF_STATE, default=self.config_entry.data[CONF_STATE]): selector.TemplateSelector(
                selector.TemplateSelectorConfig()
            )
        }

        return self.async_show_form(step_id="value_template", data_schema=vol.Schema(options_schema))
