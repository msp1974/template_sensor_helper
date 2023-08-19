from .const import TEXT_NONE
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    DEVICE_CLASS_UNITS,
    DEVICE_CLASS_STATE_CLASSES,
)
from homeassistant.helpers.template import slugify


def unslugify(text: str) -> str:
    return text.replace("_", " ").title()


def format_list(unformatted_list: list[str]) -> list[str]:
    formatted_list = []
    for item in unformatted_list:
        formatted_list.append(unslugify(item))
    return formatted_list


def get_device_class_list(sensor_type) -> list[str]:
    if sensor_type == SENSOR_DOMAIN:
        return format_list([TEXT_NONE] + sorted(list([cls.value for cls in SensorDeviceClass])))
    return format_list([TEXT_NONE] + sorted(list([cls.value for cls in BinarySensorDeviceClass])))


def get_device_class_uoms(device_class: str) -> list[str]:
    if slugify(device_class) == TEXT_NONE:
        return None
    uoms = DEVICE_CLASS_UNITS.get(slugify(device_class))
    if uoms:
        # Replace None value with text
        response = []
        for uom in uoms:
            if uom is None:
                response.append("None")
                continue
            response.append(uom)
        return response
    return []


def get_device_class_state_classes(device_class: str) -> list[str]:
    if slugify(device_class) == TEXT_NONE:
        return None
    return format_list([TEXT_NONE] + list(DEVICE_CLASS_STATE_CLASSES.get(slugify(device_class))))
