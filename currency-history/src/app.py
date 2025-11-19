import os
from datetime import UTC, datetime, timedelta

import httpx
from fastapi import FastAPI, Query

app = FastAPI(title="Currency History Service")

# Get currency-report service URL from environment variable
CURRENCY_REPORT_URL = os.getenv("CURRENCY_REPORT_URL", "http://currency-report:8100")

# Mocked historical data (last 3 days)
HISTORICAL_DATA = {
    ("USD", "BRL"): [
        {"timestamp": (datetime.now(UTC) - timedelta(days=3)).isoformat(), "price": 5.38},
        {"timestamp": (datetime.now(UTC) - timedelta(days=2)).isoformat(), "price": 5.40},
        {"timestamp": (datetime.now(UTC) - timedelta(days=1)).isoformat(), "price": 5.41},
    ],
    ("EUR", "BRL"): [
        {"timestamp": (datetime.now(UTC) - timedelta(days=3)).isoformat(), "price": 5.85},
        {"timestamp": (datetime.now(UTC) - timedelta(days=2)).isoformat(), "price": 5.87},
        {"timestamp": (datetime.now(UTC) - timedelta(days=1)).isoformat(), "price": 5.88},
    ],
}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "UP"}


@app.get("/history")
async def get_history(
    from_currency: str = Query(alias="from"),
    to_currency: str = Query(alias="to"),
) -> dict[str, str | list[dict[str, str | float]]]:
    # Get historical mocked data
    historical = HISTORICAL_DATA.get(
        (from_currency, to_currency),
        [{"timestamp": (datetime.now(UTC) - timedelta(days=1)).isoformat(), "price": 1.0}],
    )

    # Fetch current quote from currency-report service using service name
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CURRENCY_REPORT_URL}/quote", params={"from": from_currency, "to": to_currency}, timeout=5.0
            )
            response.raise_for_status()
            current_quote = response.json()

            # Add current quote to history
            values = historical + [{"timestamp": current_quote["timestamp"], "price": current_quote["price"]}]
    except Exception:
        # If currency-report is unavailable, return only historical data
        values = historical

    return {"from": from_currency, "to": to_currency, "values": values}
