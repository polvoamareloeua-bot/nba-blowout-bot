import os
import time
import requests
import threading

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 60  # 1 minuto
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ----------------------------------------------------------------
# Função de envio
# ----------------------------------------------------------------
def send(msg, chat_id=CHAT_ID):
    print(f"Enviando mensagem: {msg[:60]}...")
    try:
        url = f"{BASE_URL}/sendMessage"
        data = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar msg: {e}")

# ----------------------------------------------------------------
# Lê mensagens do Telegram (/start)
# ----------------------------------------------------------------
def listen_to_commands():
    print("Thread de comandos iniciada...")
    last_update_id = None

    while True:
        try:
            url = f"{BASE_URL}/getUpdates"
            params = {"offset": last_update_id}
            response = requests.get(url, params=params, timeout=20).json()

            if "result" in response:
                for update in response["result"]:
                    last_update_id = update["update_id"] + 1

                    if "message" in update:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"].get("text", "")

                        if text.lower().startswith("/start"):
                            send(
                                "🤖 Bot ativo!\n"
                                "Monitorando blowouts no 2º período.\n"
                                "Quando houver alerta, envio placar, probabilidade e titulares.",
                                chat_id
                            )
        except Exception as e:
            print(f"Erro thread comandos: {e}")

        time.sleep(1)

# ----------------------------------------------------------------
# Busca jogos na NBA
# ----------------------------------------------------------------
def get_games():
    print("Buscando jogos...")
    try:
        url = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
        data = requests.get(url, timeout=10).json()
        return data.get("scoreboard", {}).get("games", [])
    except Exception as e:
        print(f"Erro jogos: {e}")
        return []

# ----------------------------------------------------------------
# Busca titulares pelo ID da partida
# ----------------------------------------------------------------
def get_lineups(game_id):
    try:
        url = f"https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json"
        data = requests.get(url, timeout=10).json()

        game = data.get("game", {})
        home = game.get("homeTeam", {})
        away = game.get("awayTeam", {})

        home_starters = [p["name"] for p in home.get("players", []) if p.get("starter")]
        away_starters = [p["name"] for p in away.get("players", []) if p.get("starter")]

        return home_starters, away_starters

    except Exception as e:
        print(f"Erro lineups: {e}")
        return [], []

# ----------------------------------------------------------------
# Extração dos dados básicos
# ----------------------------------------------------------------
def extract_info(game):
    try:
        home = game["homeTeam"]
        away = game["awayTeam"]
        return {
            "game_id": game["gameId"],
            "h_team": home["teamTricode"],
            "a_team": away["teamTricode"],
            "h_score": int(home.get("score", 0)),
            "a_score": int(away.get("score", 0)),
            "period": game["period"]
        }
    except:
        return None

# ----------------------------------------------------------------
# Probabilidade simples baseada na diferença
# ----------------------------------------------------------------
def calc_probability(diff):
    if diff < 10:
        return 20
    if diff < 12:
        return 35
    if diff < 15:
        return 50
    if diff == 15:
        return 65
    if diff <= 18:
        return 78
    if diff <= 22:
        return 88
    return 95

# ----------------------------------------------------------------
# Monitoramento contínuo
# ----------------------------------------------------------------
def monitor_blowouts():
    print("Thread monitoramento iniciada!")

    while True:
        try:
            games = get_games()

            for g in games:
                info = extract_info(g)
                if not info:
                    continue

                h = info["h_score"]
                a = info["a_score"]
                diff = abs(h - a)
                period = info["period"]
                game_id = info["game_id"]

                if period == 2 and diff >= 15:
                    print("BLOWOUT ENCONTRADO!")

                    # 🟦 Titulares
                    home_starters, away_starters = get_lineups(game_id)

                    # 🟦 Probabilidade
                    prob = calc_probability(diff)

                    msg = (
                        f"🔥 *BLOWOUT DETECTADO!*\n\n"
                        f"{info['h_team']} ({h}) x {info['a_team']} ({a})\n"
                        f"Período: {period}\n"
                        f"Diferença: *{diff} pontos*\n"
                        f"Probabilidade estimada: *{prob}%*\n\n"
                        f"{info['h_team']} (titulares): {', '.join(home_starters) if home_starters else 'não disponível'}\n"
                        f"{info['a_team']} (titulares): {', '.join(away_starters) if away_starters else 'não disponível'}"
                    )

                    send(msg)

        except Exception as e:
            print(f"Erro monitoramento: {e}")
            send(f"Erro no bot: {e}")

        time.sleep(CHECK_INTERVAL)

# ----------------------------------------------------------------
# Inicialização
# ----------------------------------------------------------------

send("🤖 Bot NBA iniciado! Envie /start para ativar.")
print("Bot iniciado!")

thread1 = threading.Thread(target=listen_to_commands)
thread2 = threading.Thread(target=monitor_blowouts)

thread1.start()
thread2.start()

thread1.join()
thread2.join()
