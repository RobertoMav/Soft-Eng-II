from datetime import datetime, timezone

from fastapi import FastAPI, Query

app = FastAPI(title="Currency Report Service")

# Mocked exchange rates
EXCHANGE_RATES = {
    ("USD", "BRL"): 5.42,
    ("EUR", "BRL"): 5.89,
    ("USD", "EUR"): 0.92,
    ("BRL", "USD"): 0.18,
}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "UP"}


@app.get("/quote")
def get_quote(
    from_currency: str = Query(alias="from"),
    to_currency: str = Query(alias="to"),
) -> dict[str, str | float]:
    # Get exchange rate or default to 1.0
    rate = EXCHANGE_RATES.get((from_currency, to_currency), 1.0)

    return {
        "from": from_currency,
        "to": to_currency,
        "price": rate,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
