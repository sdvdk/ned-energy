# NED Energy

Home Assistant integration for retrieving the Dutch energy mix via the NED API.

## Installation via HACS
1. Add this repository as a custom repository in HACS (type: Integration).
2. Install the integration via HACS.
3. Add your NED API key to the configuration.

## Configuration
```yaml
sensor:
  - platform: ned_energy
    api_key: YOUR_API_KEY
```

## Features
- Retrieves the percentage of solar and wind energy per hour
- Exposes the share of green energy as a sensor in Home Assistant

## More information
See [Nationale Energie Dashboard](https://ned.nl/) for more information about the data source.
