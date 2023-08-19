# Template Sensor Helper Integration v0.1.0Beta

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![downloads](https://shields.io/github/downloads/msp1974/template_sensor/latest/total?style=for-the-badge)](https://github.com/msp1974/template_sensor)
[![version](https://shields.io/github/v/release/msp1974/template_sensor?style=for-the-badge)](https://github.com/msp1974/template_sensor)

This repository contains a Home Assistant Helper integration to provide a way to create template binary sensors and sensors via the UI, instead of having to create these by editing the configuration.yaml file.

The creation and editing of sensors should be realatively intuative but below is a basic guide of the helper and how to use it.

## Installation

This will be available via HACs in the future, but for now install via the following method.

In HACs, select integrations.  The select Custom Repositories from the 3 dots menu on the top right.

Add the following link, and select integrations as the repository type.

```text
https://github.com/msp1974/template_sensor_helper.git
```

You should then be able to download this via the usual HACs install method.

## Helper Functionality

This helper currently supports creating Binary Sensors and Sensors using templates.  It will guide you through the different elements of creating a sensor via a UI wizard and also allow you to edit all relevant parameters once created.


## Issues

This is currently a beta version and it should be expected that there maybe some issues.  Please feel free to raise these (and any suggested improvements) on the github repo.

https://github.com/msp1974/template_sensor_helper/issues

## Overview Videos

![Binary Sensor](https://github.com/msp1974/template_sensor_helper/docs/binary_template_sensor.gif)

![Sensor](https://github.com/msp1974/template_sensor_helper/docs/template_sensor.gif)