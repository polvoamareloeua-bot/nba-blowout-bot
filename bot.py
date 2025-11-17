import os
import requests
import time

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

# Mensagem inicial só para testar
send("🚀 Bot iniciado com sucesso!")

# Loop infinito só para o Render não desligar
while True:
    time.sleep(60)
