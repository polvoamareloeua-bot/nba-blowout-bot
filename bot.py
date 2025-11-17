import os
import time
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 60  # 1 minuto

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def get_games():
    """Busca jogos da NBA na API nova."""
    try:
        url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
        data = requests.get(url, timeout=10).json()
        return data.get("scoreboard", {}).get("games", [])
    except Exception as e:
        send(f"Erro ao buscar jogos: {e}")
        return []

def get_score(game):
    """Extrai placar do jogo."""
    try:
        home = game["homeTeam"]
        away = game["awayTeam"]
        return {
            "h_team": home["teamTricode"],
            "a_team": away["teamTricode"],
            "h_score": int(home.get("score", 0)),
            "a_score": int(away.get("score", 0)),
            "period": game["period"]
        }
    except:
        return None

while True:
    try:
        games = get_games()

        for g in games:
            info = get_score(g)
            if not info:
                continue

            h = info["h_score"]
            a = info["a_score"]
            diff = abs(h - a)
            period = info["period"]

            if period == 2 and diff >= 15:
                send(
                    f"🔥 *BLOWOUT DETECTADO!*\n\n"
                    f"{info['h_team']} ({h}) x {info['a_team']} ({a})\n"
                    f"Período: {period}\n"
                    f"Diferença: {diff} pontos\n"
                )

    except Exception as e:
        send(f"Erro no bot: {e}")

    time.sleep(CHECK_INTERVAL)
