import json
import os
import time
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

TESLA_URL = "https://www.tesla.com/inventory/api/v4/inventory-results"

MODELS = ["m3", "my", "ms", "mx"]

DATABASE = "seen_teslas.json"


def telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    r = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False,
        },
        timeout=20,
    )

    print("Telegram:", r.status_code)

    if r.status_code != 200:
        print(r.text)


def load_seen():
    try:
        with open(DATABASE, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_seen(seen):
    with open(DATABASE, "w") as f:
        json.dump(sorted(seen), f, indent=2)


def search_model(session, model):

    query = {
        "query": {
            "model": model,
            "condition": "new",
            "options": {},
            "arrangeby": "Price",
            "order": "asc",
            "market": "FR",
            "language": "fr",
            "super_region": "europe",
            "lng": "",
            "lat": "",
            "zip": "",
            "range": 0,
        },
        "offset": 0,
        "count": 100,
        "outsideOffset": 0,
        "outsideSearch": False,
        "isFalconDeliverySelectionEnabled": True,
        "version": "v2",
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Referer": "https://www.tesla.com/fr_fr/inventory/new/",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
    }

    response = session.get(
        TESLA_URL,
        params={"query": json.dumps(query)},
        headers=headers,
        timeout=30,
    )

    print(f"Tesla {model}: HTTP {response.status_code}")

    if response.status_code != 200:
        print(response.text[:500])
        return []

    data = response.json()

    results = data.get("results", [])

    if not isinstance(results, list):
        return []

    return results


def main():

    print("=== TESLA ALERT ===")

    session = requests.Session()

    # Première visite du site Tesla pour récupérer d'éventuels cookies
    try:
        session.get(
            "https://www.tesla.com/fr_fr/inventory/new/",
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                )
            },
            timeout=30,
        )
    except Exception as e:
        print("Visite Tesla:", e)

    seen = load_seen()
    new_cars = []

    for model in MODELS:

        try:
            cars = search_model(session, model)

            print(f"{model}: {len(cars)} véhicules")

            for car in cars:

                vin = (
                    car.get("VIN")
                    or car.get("vin")
                    or car.get("VINNumber")
                )

                if not vin:
                    continue

                if vin in seen:
                    continue

                name = (
                    car.get("Model")
                    or car.get("model")
                    or model.upper()
                )

                price = (
                    car.get("Price")
                    or car.get("price")
                    or "?"
                )

                trim = (
                    car.get("TrimName")
                    or car.get("trimName")
                    or ""
                )

                color = (
                    car.get("Color")
                    or car.get("color")
                    or ""
                )

                city = (
                    car.get("City")
                    or car.get("city")
                    or ""
                )

                url = (
                    car.get("VehicleURL")
                    or car.get("vehicleUrl")
                    or ""
                )

                new_cars.append({
                    "vin": vin,
                    "model": name,
                    "price": price,
                    "trim": trim,
                    "color": color,
                    "city": city,
                    "url": url,
                })

        except Exception as e:
            print(f"Erreur {model}:", e)

    # Mémorise les véhicules
    for model in MODELS:
        try:
            cars = search_model(session, model)

            for car in cars:
                vin = (
                    car.get("VIN")
                    or car.get("vin")
                    or car.get("VINNumber")
                )

                if vin:
                    seen.add(vin)

        except Exception:
            pass

    save_seen(seen)

    print(f"Nouvelles Tesla: {len(new_cars)}")

    # Telegram
    for car in new_cars[:10]:

        message = (
            "🚨 NOUVELLE TESLA DISPONIBLE 🇫🇷\n\n"
            f"🚗 {car['model']}\n"
            f"⚙️ {car['trim']}\n"
            f"💰 {car['price']} €\n"
            f"🎨 {car['color']}\n"
            f"📍 {car['city']}\n"
            f"🆔 {car['vin']}"
        )

        if car["url"]:
            message += f"\n\n🔗 {car['url']}"

        telegram(message)

        time.sleep(1)


if __name__ == "__main__":
    main()