import os

template_py = """
import asyncio
from telethon import TelegramClient, events

api_id = {api_id}
api_hash = "{api_hash}"
phone_number = "{phone_number}"

source_chat_id = {source_id}
destination_channel_id = {dest_id}
keywords = {keywords}

client = TelegramClient('session_{phone_number}', api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat_id))
async def handler(event):
    text = event.message.message.lower()
    if keywords:
        if event.message.text and any(k.lower() in text for k in keywords):
            await client.send_message(destination_channel_id, event.message.text)
    else:
        await client.send_message(destination_channel_id, event.message.text)

print("🔍 Monitoraggio avviato...")
client.start()
client.run_until_disconnected()
"""

template_sh = """#!/bin/bash
# --- Script per avviare il bot Telegram in background senza virtualenv ---

PYTHON=$(which python3)
BOT_SCRIPT="{py_file}"
LOG_FILE="${BOT_SCRIPT}.log"

echo "Verifica installazione Telethon..."
$PYTHON -m pip show telethon > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Telethon non trovato, installo..."
    $PYTHON -m pip install --break-system-packages --upgrade pip
    $PYTHON -m pip install telethon --break-system-packages
fi

echo "Avvio del bot in background..."
nohup $PYTHON "$BOT_SCRIPT" > "$LOG_FILE" 2>&1 &
echo "Bot avviato. Log in $LOG_FILE"
"""

# --- Inserimento dati dall'utente ---
api_id = input("Inserisci API ID: ")
api_hash = input("Inserisci API Hash: ")
phone_number = input("Inserisci numero di telefono: ")
source_id = int(input("Inserisci ID del canale sorgente: "))
dest_id = int(input("Inserisci ID del canale destinazione: "))
kw_input = input("Inserisci parole chiave separate da virgola (o lascia vuoto per tutte): ")
keywords = [k.strip() for k in kw_input.split(",")] if kw_input else []

# --- Generazione file Python ---
py_filename = f"forwarder_{source_id}_{dest_id}.py"
with open(py_filename, "w", encoding="utf-8") as f:
    f.write(template_py.format(api_id=api_id, api_hash=api_hash, phone_number=phone_number,
                               source_id=source_id, dest_id=dest_id, keywords=keywords))

# --- Generazione file SH ---
sh_filename = f"start_forwarder_{source_id}_{dest_id}.sh"
with open(sh_filename, "w", encoding="utf-8") as f:
    f.write(template_sh.format(py_file=py_filename))

os.chmod(sh_filename, 0o755)

print(f"✅ File generati:")
print(f" - Script Python: {py_filename}")
print(f" - Script avvio background: {sh_filename}")
print(f"Avvia il bot con: bash {sh_filename}")
