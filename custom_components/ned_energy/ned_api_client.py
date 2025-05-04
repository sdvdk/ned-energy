import os
import httpx
from datetime import datetime, timedelta
import json

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

async def async_get_energy_mix(api_key):
    now = datetime.now()
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    client = NEDClient(api_key)
    # Type IDs for main sources (example IDs, adjust as needed)
    energy_types = {
        "solar": 2,
        "wind": 1,
        "wind_offshore": 17,
        "coal": 4,
        "gas": 5,
        "nuclear": 6,
        "biomass": 7,
        "hydro": 8,
        "other": 9
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
                result[timestamp] = {k: 0 for k in energy_types.keys()}
            value = float(entry.get("volume", 0))
            result[timestamp][name] = value
    processed_result = []
    for timestamp, values in sorted(result.items()):
        green = values['solar'] + values['wind'] + values['wind_offshore']
        wind_total = values['wind'] + values['wind_offshore']
        total = sum(values.values())
        green_percentage = (green / total * 100) if total > 0 else 0
        solar_percentage = (values['solar'] / total * 100) if total > 0 else 0
        wind_percentage = (wind_total / total * 100) if total > 0 else 0
        
        # Calculate percentages for all sources
        source_percentages = {
            f"{source}_percentage": (value / total * 100) if total > 0 else 0
            for source, value in values.items()
        }
        
        processed_result.append({
            'timestamp': timestamp,
            'solar_volume': values['solar'],
            'wind_volume': wind_total,
            'wind_offshore_volume': values['wind_offshore'],
            'coal_volume': values['coal'],
            'gas_volume': values['gas'],
            'nuclear_volume': values['nuclear'],
            'biomass_volume': values['biomass'],
            'hydro_volume': values['hydro'],
            'other_volume': values['other'],
            'green_percentage': green_percentage,
            'solar_percentage': solar_percentage,
            'wind_percentage': wind_percentage,
            **source_percentages,  # Include all source percentages
            'total_volume': total
        })
    return processed_result

if __name__ == "__main__":
    import asyncio
    import os
    api_key = os.getenv("NED_API_KEY")
    if not api_key:
        print("Please set the NED_API_KEY environment variable.")
    else:
        async def main():
            data = await async_get_energy_mix(api_key)
            print("\nNED Energy Mix Data (24 hours):")
            print(json.dumps(data, indent=2))
            
            # Print summary statistics for all sources
            print("\nSummary Statistics:")
            sources = ['solar', 'wind', 'wind_offshore', 'coal', 'gas', 'nuclear', 'biomass', 'hydro', 'other']
            total_production = sum(entry['total_volume'] for entry in data)
            
            for source in sources:
                volume = sum(entry[f'{source}_volume'] for entry in data)
                percentage = (volume / total_production * 100) if total_production > 0 else 0
                print(f"{source.title()} Production: {volume:,.0f} kWh ({percentage:.1f}%)")
            
            print(f"\nTotal Production: {total_production:,.0f} kWh")
            avg_green_percentage = sum(entry['green_percentage'] for entry in data) / len(data)
            print(f"Average Green Percentage: {avg_green_percentage:.1f}%")
            
        asyncio.run(main()) 