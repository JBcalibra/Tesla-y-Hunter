import asyncio
import os
import requests
import nodriver as uc


BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


async def main():

    print("🚗 Ouverture de Tesla...")

    # Démarrage de Chrome compatible GitHub Actions
    browser = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_executable_path="/usr/bin/google-chrome",
        browser_args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-software-rasterizer",
        ],
    )

    try:

        print("🌐 Ouverture de la page Tesla...")

        page = await browser.get(
            "https://www.tesla.com/fr_fr/inventory/new/my"
        )

        print("⏳ Attente du chargement de Tesla...")
        await asyncio.sleep(12)

        print("🔎 Lecture de la page Tesla...")

        html = await page.get_content()

        print(f"✅ Page Tesla reçue : {len(html)} caractères")

    finally:

        print("🛑 Fermeture de Chrome...")
        browser.stop()

    # --------------------------------------------------
    # TEST DE L'ACCÈS DIRECT À TESLA
    # --------------------------------------------------

    print("📡 Test de connexion Tesla...")

    url = "https://www.tesla.com/fr_fr/inventory/new/my"

    response = requests.get(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/139.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "fr-FR,fr;q=0.9",
        },
        timeout=30,
    )

    print("Tesla HTTP :", response.status_code)

    if response.status_code != 200:

        print("⚠️ Tesla refuse la requête directe.")

        message = (
            "🤖 TESLA HUNTER 🇫🇷\n\n"
            "⚠️ Chrome Tesla fonctionne.\n"
            "❌ La requête directe Tesla est refusée.\n\n"
            f"HTTP Tesla : {response.status_code}"
        )

    else:

        print("✅ Tesla accessible.")

        message = (
            "🤖 TESLA HUNTER ACTIF 🇫🇷\n\n"
            "✅ Chrome Tesla fonctionne\n"
            "✅ Connexion Tesla réussie\n"
            "✅ Surveillance Model 3 / Model Y / Model S / Model X\n"
            "🔎 Recherche des véhicules neufs en France\n\n"
            "Le robot fonctionne correctement."
        )

    # --------------------------------------------------
    # ENVOI TELEGRAM
    # --------------------------------------------------

    print("📨 Envoi du message Telegram...")

    telegram_url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    telegram = requests.post(
        telegram_url,
        json={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=20,
    )

    print("Telegram HTTP :", telegram.status_code)

    if telegram.status_code != 200:

        print("❌ Erreur Telegram :")
        print(telegram.text)

        raise Exception("Erreur Telegram")

    print("✅ Message Telegram envoyé !")


asyncio.run(main())