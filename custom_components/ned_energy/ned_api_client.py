import os
import httpx
from datetime import datetime, timedelta

class NEDClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.ned.nl/v1"
        self.headers = {
            "X-AUTH-TOKEN": self.api_key,
            "accept": "application/ld+json"
        }

    async def get_utilization_data(self, point, type_id, start_date, end_date, granularity="Hour"):
        params = {
            "itemsPerPage": 200,
            "point": point,
            "type": type_id,
            "classification": 2,
            "granularity": 5,
            "granularitytimezone": 1,
            "activity": 1,
            "validfrom[strictly_before]": end_date.strftime("%Y-%m-%d"),
            "validfrom[after]": start_date.strftime("%Y-%m-%d")
        }
        async with httpx.AsyncClient(verify=False, headers=self.headers) as client:
            try:
                response = await client.get(f"{self.base_url}/utilizations", params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("hydra:member", [])
            except Exception:
                return []

async def async_get_energy_mix(api_key, days=1):
    if not api_key:
        api_key = os.getenv('NED_API_KEY')
    if not api_key:
        raise ValueError("NED_API_KEY not found in environment variables or .env file")
    client = NEDClient(api_key)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    try:
        energy_types = {
            "solar": 2,
            "wind": 1,
            "wind_offshore": 17
        }
        result = {}
        for name, type_id in energy_types.items():
            data = await client.get_utilization_data(
                point=0,
                type_id=type_id,
                start_date=start_date,
                end_date=end_date
            )
            for entry in data:
                timestamp = entry.get("validfrom")
                if not timestamp:
                    continue
                if timestamp not in result:
                    result[timestamp] = {
                        'solar': 0,
                        'wind': 0,
                        'wind_offshore': 0
                    }
                value = float(entry.get("percentage", 0))
                result[timestamp][name] = value
        processed_result = []
        for timestamp, values in sorted(result.items()):
            total_wind = values['wind'] + values['wind_offshore']
            total = values['solar'] + total_wind
            if total > 0:
                processed_result.append({
                    'timestamp': timestamp,
                    'solar_percentage': values['solar'],
                    'wind_percentage': total_wind,
                    'green_percentage': 100
                })
        return processed_result
    except Exception as e:
        return None

if __name__ == "__main__":
    import asyncio
    import os
    api_key = os.getenv("NED_API_KEY")
    if not api_key:
        print("Please set the NED_API_KEY environment variable.")
    else:
        async def main():
            data = await async_get_energy_mix(api_key, days=1)
            print("NED Energy Mix Data:")
            for entry in data:
                print(entry)
        asyncio.run(main()) 