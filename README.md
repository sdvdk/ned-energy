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

## More information
See [Nationale Energie Dashboard](https://ned.nl/) for more information about the data source.
