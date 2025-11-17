import os
import time
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 60  # 1 minuto

def send(msg):
    print(f"Enviando para Telegram: {msg[:50]}...")
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def get_games():
    print("Buscando jogos da NBA...")
    try:
        url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
        data = requests.get(url, timeout=10).json()
        return data.get("scoreboard", {}).get("games", [])
    except Exception as e:
        print(f"Erro ao buscar jogos: {e}")
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

# Mensagem inicial
send("🤖 Bot NBA iniciado e monitorando jogos! Envie /start para confirmar.")

print("Bot iniciado com sucesso!")
print("Iniciando monitoramento...")

while True:
    try:
        print("Checando jogos...")
        games = get_games()

        for g in games:
            info = get_score(g)
            if not info:
                continue

            h = info["h_score"]
            a = info["a_score"]
