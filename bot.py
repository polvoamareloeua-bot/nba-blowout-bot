import os
import time
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 60  # segundos

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

def get_games():
    try:
        today = requests.get("https://data.nba.net/prod/v2/today.json").json()
        scoreboard_url = today["links"]["scoreboard"]
        games = requests.get("https://data.nba.net" + scoreboard_url).json()
        return games["games"]
    except:
        return []

def get_starters(game):
    try:
        h = game["hTeam"]["triCode"]
        v = game["vTeam"]["triCode"]
        return f"Titulares ainda não implementados"
    except:
        return "Sem informação"

while True:
    try:
        games = get_games()

        for g in games:
            period = g["period"]["current"]
            h = int(g["hTeam"]["score"] or 0)
            v = int(g["vTeam"]["score"] or 0)
            diff = abs(h - v)

            if period == 2 and diff >= 15:
                send(
                    f"🔥 **BLOWOUT DETECTADO!**\n\n"
                    f"{g['vTeam']['triCode']} ({v}) x ({h}) {g['hTeam']['triCode']}\n"
                    f"Período: {period}\n"
                    f"Diferença: {diff} pontos\n\n"
                    f"Titulares:\n{get_starters(g)}"
                )

    except Exception as e:
        send(f"Erro no bot: {e}")

    time.sleep(CHECK_INTERVAL)
