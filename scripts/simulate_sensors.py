import asyncio
import random
import time
from datetime import datetime, timezone
import httpx


API_URL = "http://127.0.0.1:8000/api/sensors/readings"

SENSORS_CONFIG = [
    {
        "sensor_id": "WP-001",
        "type": "WATER_PRESSURE",
        "unit": "psi",
        "normal_range": (52.0, 58.0),
        "anomaly_range": (82.0, 92.0),
        "anomaly_prob": 0.35,  # Higher probability for interactive demo
    },
    {
        "sensor_id": "FL-001",
        "type": "FLOW",
        "unit": "L/min",
        "normal_range": (180.0, 220.0),
        "anomaly_range": (35.0, 50.0),  # Sudden drop indicates burst/blockage
        "anomaly_prob": 0.20,
    },
    {
        "sensor_id": "VIB-001",
        "type": "VIBRATION",
        "unit": "mm/s",
        "normal_range": (0.8, 1.8),
        "anomaly_range": (5.2, 7.8),
        "anomaly_prob": 0.20,
    },
    {
        "sensor_id": "WL-001",
        "type": "WATER_LEVEL",
        "unit": "m",
        "normal_range": (1.2, 2.5),
        "anomaly_range": (5.8, 7.2),
        "anomaly_prob": 0.15,
    },
]


async def send_reading(client: httpx.AsyncClient, sensor: dict, force_anomaly: bool = False):
    """Generate reading and post to API."""
    is_anomaly_run = force_anomaly or (random.random() < sensor["anomaly_prob"])

    if is_anomaly_run:
        val = random.uniform(*sensor["anomaly_range"])
    else:
        val = random.uniform(*sensor["normal_range"])

    payload = {
        "sensor_id": sensor["sensor_id"],
        "value": round(val, 2),
        "unit": sensor["unit"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "quality": "GOOD",
        "metadata": {
            "simulator": True,
            "device": "SIMULATED_ARDUINO_ESP32",
            "simulated_anomaly": is_anomaly_run
        }
    }

    try:
        res = await client.post(API_URL, json=payload)
        if res.status_code == 201:
            data = res.json()
            anom_flag = "[ANOMALY DETECTED!]" if data.get("is_anomaly") else "[NORMAL]"
            warn_flag = f"--> Warning #{data.get('warning_id')} Generated!" if data.get("warning_generated") else ""
            print(f"[{sensor['sensor_id']}] Sent {val:.1f} {sensor['unit']} | Status: {anom_flag} {warn_flag} (Asset Risk: {data.get('asset_risk_score', 'N/A')})")
        else:
            print(f"[{sensor['sensor_id']}] Error: HTTP {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[{sensor['sensor_id']}] Connection Error (Is backend running on port 8000?): {e}")


async def run_simulation(iterations: int = 10, interval_seconds: float = 2.0):
    """Run sensor simulator loop."""
    print("=" * 70)
    print(" SMARTINFRA AI - IoT SENSOR SIMULATOR (PUNE INFRASTRUCTURE)")
    print(f" Target API: {API_URL}")
    print(f" Simulating: {[s['sensor_id'] for s in SENSORS_CONFIG]}")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=5.0) as client:
        # First send a guaranteed normal baseline
        print("\n--- Phase 1: Sending Normal Telemetry Baseline ---")
        for s in SENSORS_CONFIG:
            await send_reading(client, s, force_anomaly=False)
            await asyncio.sleep(0.5)

        # Send an intentional anomaly on WP-001 (Water Pressure Spike)
        print("\n--- Phase 2: Injecting Water Pressure Spike Anomaly on PUN-PIPE-001 (WP-001) ---")
        wp_sensor = SENSORS_CONFIG[0]
        await send_reading(client, wp_sensor, force_anomaly=True)
        await asyncio.sleep(1.0)

        # Simulation loop
        print(f"\n--- Phase 3: Continuous IoT Simulation ({iterations} rounds, {interval_seconds}s interval) ---")
        for i in range(1, iterations + 1):
            print(f"\n>> Round {i}/{iterations}:")
            for s in SENSORS_CONFIG:
                await send_reading(client, s)
                await asyncio.sleep(0.3)
            await asyncio.sleep(interval_seconds)

    print("\nSimulation completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_simulation(iterations=5, interval_seconds=1.5))
