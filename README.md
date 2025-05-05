# NED Energy

Home Assistant integration for retrieving the Dutch energy mix via the NED API.

## Features
- Asynchronous, periodic updates (every 15 minutes by default)
- Three separate sensors:
  - Solar Percentage
  - Wind Percentage (onshore + offshore)
  - Green Energy Percentage (total)
- Easy setup via the Home Assistant UI (config flow)
- No YAML configuration required

## Installation via HACS
1. Add this repository as a custom repository in HACS (type: Integration).
2. Install the integration via HACS.
3. In Home Assistant, go to **Settings → Devices & Services → Add Integration** and search for **NED Energy**.
4. Enter your NED API key when prompted.

## Example: Green Energy Mix Chart

You can visualize the data for today using [ApexCharts Card](https://github.com/RomRider/apexcharts-card) in your Home Assistant dashboard.

```yaml
type: custom:apexcharts-card
graph_span: 24h
span:
  start: day
header:
  title: Dutch Green Energy Mix
  show: true
all_series_config:
  type: column
series:
  - name: Solar
    entity: sensor.ned_solar_percentage
    color: "#f1c40f"
    data_generator: |
      if (!entity.attributes.today_data) return [];
      return entity.attributes.today_data.map(d => [
        new Date(d.timestamp).getTime(),
        d.solar_percentage
      ]);
  - name: Wind
    entity: sensor.ned_wind_percentage
    color: "#2980b9"
    data_generator: |
      if (!entity.attributes.today_data) return [];
      return entity.attributes.today_data.map(d => [
        new Date(d.timestamp).getTime(),
        d.wind_percentage
      ]);
  - name: Biomass
    entity: sensor.ned_biomass_percentage
    color: "#2ecc71"
    data_generator: |
      if (!entity.attributes.today_data) return [];
      return entity.attributes.today_data.map(d => [
        new Date(d.timestamp).getTime(),
        d.biomass_percentage
      ]);
  - name: Hydro
    entity: sensor.ned_hydro_percentage
    color: "#3498db"
    data_generator: |
      if (!entity.attributes.today_data) return [];
      return entity.attributes.today_data.map(d => [
        new Date(d.timestamp).getTime(),
        d.hydro_percentage
      ]);
yaxis:
  - min: 0
    decimals: 1
    apex_config:
      tickAmount: 10
```

## Example: Gray Energy Mix Chart

```yaml
type: custom:apexcharts-card
graph_span: 24h
span:
  start: day
header:
  title: Dutch Gray Energy Mix
  show: true
all_series_config:
  type: column
series:
  - name: Coal
    entity: sensor.ned_coal_percentage
    color: "#7f8c8d"
    data_generator: |
      if (!entity.attributes.today_data) return [];
      return entity.attributes.today_data.map(d => [
        new Date(d.timestamp).getTime(),
        d.coal_percentage
      ]);
  - name: Gas
    entity: sensor.ned_gas_percentage
    color: "#e74c3c"
    data_generator: |
      if (!entity.attributes.today_data) return [];
      return entity.attributes.today_data.map(d => [
        new Date(d.timestamp).getTime(),
        d.gas_percentage
      ]);
  - name: Nuclear
    entity: sensor.ned_nuclear_percentage
    color: "#9b59b6"
    data_generator: |
      if (!entity.attributes.today_data) return [];
      return entity.attributes.today_data.map(d => [
        new Date(d.timestamp).getTime(),
        d.nuclear_percentage
      ]);
  - name: Other
    entity: sensor.ned_other_percentage
    color: "#95a5a6"
    data_generator: |
      if (!entity.attributes.today_data) return [];
      return entity.attributes.today_data.map(d => [
        new Date(d.timestamp).getTime(),
        d.other_percentage
      ]);
yaxis:
  - min: 0
    decimals: 1
    apex_config:
      tickAmount: 10
```

## More information
See [Nationale Energie Dashboard](https://ned.nl/) for more information about the data source.
