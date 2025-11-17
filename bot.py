import os
import time
import requests
import threading

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 60  # minutos para checar blowout

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ---------------------------------------------------------
# Envio de mensagens
# ---------------------------------------------------------
def send(msg, chat_id=CHAT_ID):
    print(f"Enviando mensagem: {msg[:60]}...")
    try:
        url = f"{BASE_URL}/sendMessage"
        data = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")


# ---------------------------------------------------------
# Leitura de mensagens do Telegram (para comando /start)
# ---------------------------------------------------------
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

                        # Comando /start
                        if text.lower().startswith("/start"):
                            send("🤖 Bot ativo! Vou monitorar jogos e avisar blowouts no 2º quarto!", chat_id)

        except Exception as e:
            print(f"Erro na thread de comandos: {e}")

        time.sleep(1)


# ---------------------------------------------------------
# Monitoramento de partidas
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Thread principal: verificação de blowout
# ---------------------------------------------------------
def monitor_blowouts():
    print("Thread de monitoramento iniciada!")

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
                        f"Diferença: *{diff}* pontos\n"
                    )
                else:
                    print("Nenhum blowout.")

        except Exception as e:
            print(f"Erro geral no loop: {e}")
            send(f"Erro no bot: {e}")

        print("Aguardando 1 minuto...\n")
        time.sleep(CHECK_INTERVAL)


# ---------------------------------------------------------
# Inicialização
# ---------------------------------------------------------
send("🤖 Bot NBA iniciado! Envie /start para ativar no seu chat.")
print("Bot iniciado com sucesso!")

# Criar threads
thread_commands = threading.Thread(target=listen_to_commands)
thread_monitor = threading.Thread(target=monitor_blowouts)

# Ativa as duas em paralelo
thread_commands.start()
thread_monitor.start()

# Impede o processo principal de encerrar
thread_commands.join()
thread_monitor.join()
