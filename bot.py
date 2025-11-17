import os
import time
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 60  # 1 minuto

def send(msg):
    print(f"Enviando mensagem: {msg[:50]}...")
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
        response = requests.get(url, timeout=10)
        data = response.json()
        return data.get("scoreboard", {}).get("games", [])
    except Exception as e:
        print(f"Erro ao buscar jogos: {e}")
        send(f"Erro ao buscar jogos: {e}")
        return []

def get_score(game):
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
    except Exception as e:
        print(f"Erro ao extrair placar: {e}")
        return None

send("🤖 Bot NBA iniciado e monitorando jogos!")

print("Bot iniciado com sucesso!")
print("Monitorando jogos...")

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
            diff = abs(h - a)
            period = info["period"]

            if period == 2 and diff >= 15:
                print(f"BLOWOUT detectado! Diferença {diff}")
                send(
                    f"🔥 *BLOWOUT DETECTADO!*\n\n"
                    f"{info['h_team']} ({h}) x {info['a_team']} ({a})\n"
                    f"Período: {period}\n"
                    f"Diferença: {diff} pontos\n"
                )
            else:
                print("Nenhum blowout.")

    except Exception as e:
        print(f"Erro geral no loop: {e}")
        send(f"Erro no bot: {e}")

    print("Aguardando 1 minuto...\n")
    time.sleep(CHECK_INTERVAL)
