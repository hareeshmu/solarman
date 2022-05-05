# ⚡ solarman

![Solarman Workflow](https://github.com/hareeshmu/solarman/actions/workflows/image.yml/badge.svg)  [![solarman docker image size](https://img.shields.io/docker/image-size/hareeshmu/solarman?style=flat-square)](https://hub.docker.com/r/hareeshmu/solarman "solarman docker image size")  [![Total DockerHub pulls](https://img.shields.io/docker/pulls/hareeshmu/solarman?style=flat-square)](https://hub.docker.com/r/hareeshmu/solarman "Total DockerHub pulls")

Script to retrieve current Solar PV data from the Solarman API, and send Power (W) and Energy (kWh) metrics to a MQTT broker, for further use in home automation. Several PV vendors use the Solarman Smart platform for statistics, like sofar inverter with logger.

```lang=bash
usage: run.py [--repeat]

Collect data from Solarman API

optional arguments:
--repeat                       Repeat at every interval defined in the config
```

## Usage

You can run this script as a Docker container or in Python 3. Either way a configuration file is required. See the sample `config.sample.json` file in this repository for reference. Also, a Solarman API appid and secret is required, which can be requested via <mailto:service@solarmanpv.com>.

### Using Docker

Supported platforms:

* linux/amd64
* linux/386
* linux/arm/v7
* linux/arm/v6
* linux/arm64

Docker example to run this script every 5 minutes and providing a config file:

```lang=bash
cd /opt
git clone https://github.com/hareeshmu/solarman
cd solarman
mv config.sample.json config.json # setup your config
sudo docker run --name solarman -d --restart unless-stopped -v /YOUR/PATH/HERE/config.json:/config.json hareeshmu/solarman:latest
```

### Using docker-compose

This `docker-compose.yml` example can be used with docker-compose or podman-compose

```lang=yaml
version: "3.7"
services:
  solarman:
    image: hareeshmu/solarman:latest
    container_name: solarman
    environment:
      - PUID=1000
      - PGID=1000
    volumes:
      - /YOUR/PATH/HERE/config.json:/config.json
    restart: unless-stopped
```

### Using Python

Run `pip install -r requirements.txt` and start `python3 solarman.py`.

Run `pip install -r requirements.txt` and start `python3 solarman.py --repeat`.

## MQTT topics

### Station (Plant)

```lang=bash
solarmanpv/station/batteryPower
solarmanpv/station/batterySoc
solarmanpv/station/chargePower
solarmanpv/station/dischargePower
solarmanpv/station/generationPower
solarmanpv/station/gridPower
solarmanpv/station/irradiateIntensity
solarmanpv/station/lastUpdateTime
solarmanpv/station/purchasePower
solarmanpv/station/usePower
solarmanpv/station/wirePower
```

### Inverter

```lang=bash
solarmanpv/inverter/deviceId
solarmanpv/inverter/deviceSn
solarmanpv/inverter/deviceState
solarmanpv/inverter/deviceType

solarmanpv/inverter/attributes # contains all inverter datalist entries.
```

#### Inverter Attributes

```lang=bash
SN: XXXXXXXXXX
Device_Type: 4
Production_Compliance_Type: 0
Rated_Power: 300.00
Year: 48
Month: 0
Day: 0
Hour: 0
Minute: 0
Seconds: 0
Communication_Protocol_Version: V0.2.0.1
Control_Board_Firmware_Version: V0.1.1.2
Communication_Board_Firmware_Version: V0.2.0.7
DC_Voltage_PV1: 0.00
DC_Voltage_PV2: 0.00
DC_Voltage_PV3: 0.00
DC_Voltage_PV4: 0.00
DC_Current_PV1: 0.00
DC_Current_PV2: 0.00
DC_Current_PV3: 0.00
DC_Current_PV4: 0.00
DC_Power_PV1: 0.00
DC_Power_PV2: 0.00
DC_Power_PV3: 0.00
DC_Power_PV4: 0.00
AC_Voltage_1: 0.00
AC_Current_1: 0.00
Total_AC_Output_Power(Active): 0
AC_Output_Frequency_1: 0.00
Total_Production(Active): 2.50
Total_Production_1: 2.50
Total_Production_2: 0.00
Total_Production_3: 0.00
Total_Production_4: 0.00
Daily_Production(Active): 0.70
Daily_Production_1: 0.70
Daily_Production_2: 0.00
Daily_Production_3: 0.00
Daily_Production_4: 0.00
AC_Radiator_Temp: -10.00
Micro_Inverter_Port_1: XXXXXXXXXX-1
Micro_Inverter_Port_2: XXXXXXXXXX-2
Micro_Inverter_Port_3: XXXXXXXXXX-3
Micro_Inverter_Port_4: XXXXXXXXXX-4
Number_Of_MPPT_Paths: 1
Number_Of_Phases: 1
Running_Status: 4
Overfrequency_And_Load_Reduction_Starting_Point: 50.20
Islanding Protection Enabled: Enable
Overfrequency_And_Load_Reduction_Percentage: 44
GFDI Enabled: Disable
Grid-connected Standard: 0
Grid Voltage_Upper_Limit: 275.00
Grid Voltage_Lower_Limit: 180.00
Grid Frequency_Upper_Limit: 52.00
Grid Frequency_Lower_Limit: 47.50
Start-up Self-checking Time: 60
```

### Logger (Collector)

```lang=bash
solarmanpv/logger/deviceId
solarmanpv/logger/deviceSn
solarmanpv/logger/deviceState
solarmanpv/logger/deviceType

solarmanpv/logger/attributes # contains all logger datalist entries
```

#### Logger Attributes

```lang=bash
Embedded_Device_SN: XXXXXXXXXX
Module_Version_No: MW3_15_5406_1.35
Extended_System_Version: V1.1.00.07
Total_running_time: 1
Offset_time: 1634486607
Data_Uploading_Period: 5
Data_Acquisition_Period: 60
Max._No._of_Connected_Devices: 1
Signal_Strength: 100
Heart_Rate: 120
IV_Curve_Supported: 1
Batch_Command_Supported: 1
Support_Reporting_Upgrading_Progress: 0
AT+UPGRADE_Command_Supported: 255
Method_Of_Protocol_Upgrade: 255
```

## Home Assistant

```lang=bash
sensor:
  - platform: mqtt
    name: "solarmanpv_station_generationPower"
    state_topic: "solarmanpv/station/generationPower"
    unit_of_measurement: "W"
    state_class: measurement
```

Repeat for every station topic needed.

```lang=bash
sensor:
  - platform: mqtt
    name: "solarmanpv_inverter"
    state_topic: "solarmanpv/inverter/deviceState"
    json_attributes_topic: "solarmanpv/inverter/attributes"
    
  - platform: mqtt
    name: "solarmanpv_logger"
    state_topic: "solarmanpv/logger/deviceState"
    json_attributes_topic: "solarmanpv/logger/attributes"

  - platform: template
    sensors:
      solarmanpv_inverter_device_state:
        entity_id: sensor.solarmanpv_inverter
        value_template: >-
          {% set mapper =  {
              '1' : 'Online',
              '2' : 'Failure',
              '3' : 'Offline'} %}
          {% set state =  states.sensor.solarmanpv_inverter.state %}
          {{ mapper[state] if state in mapper else 'Unknown' }}
         
  - platform: template
    sensors:
      solarmanpv_logger_device_state:
        entity_id: sensor.solarmanpv_logger
        value_template: >-
          {% set mapper =  {
              '1' : 'Online',
              '2' : 'Failure',
              '3' : 'Offline'} %}
          {% set state =  states.sensor.solarmanpv_logger.state %}
          {{ mapper[state] if state in mapper else 'Unknown' }}

```

### Templates

```lang=bash
template:
  - sensor:
    - name: solarmanpv_inverter_dc_voltage_pv1
      unit_of_measurement: 'V'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Voltage_PV1') }}"
      state_class: measurement
  - sensor:
    - name: solarmanpv_inverter_dc_current_pv1
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Current_PV1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_dc_power_pv1
      unit_of_measurement: 'W'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Power_PV1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_dc_power_pv1
      unit_of_measurement: 'W'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Power_PV1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_total_production_1
      unit_of_measurement: 'kWh'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'Total_Production_1') }}"
      state_class: total_increasing
      
  - sensor:
    - name: solarmanpv_inverter_daily_production_1
      unit_of_measurement: 'kWh'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'Daily_Production_1') }}"
      state_class: total_increasing

  - sensor:
    - name: solarmanpv_inverter_ac_radiator_temp
      unit_of_measurement: '°C'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Radiator_Temp') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_ac_voltage_1
      unit_of_measurement: 'V'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Voltage_1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_ac_current_1
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Current_1') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_ac_output_frequency_1
      unit_of_measurement: 'Hz'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Output_Frequency_1') }}"
      state_class: measurement

```
