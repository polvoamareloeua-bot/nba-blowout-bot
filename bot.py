import os
import time
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 20  # segundos
send("Bot iniciado com sucesso! 🚀")
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_games():
    url = "https://data.nba.net/prod/v2/today.json"
    today = requests.get(url).json()["links"]["scoreboard"]
    sb = requests.get("https://data.nba.net" + today).json()
    return sb["games"]

while True:
    try:
        games = get_games()
        for g in games:
            period = g["period"]["current"]
            h = int(g["hTeam"]["score"] or 0)
            v = int(g["vTeam"]["score"] or 0)
            diff = abs(h - v)

            if period == 2 and diff >= 15:
                send(f"BLOWOUT NBA\nJogo: {g['vTeam']['triCode']} @ {g['hTeam']['triCode']}\nPlacar: {v} x {h}\nPeríodo: 2º\nDiferença: {diff} pontos")
    except Exception as e:
        print("Erro:", e)

    time.sleep(CHECK_INTERVAL)
