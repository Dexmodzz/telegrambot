import os
import asyncio
from telethon import TelegramClient, events

CREDENTIALS_FILE = "credentials.txt"

def read_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            if len(lines) == 3:
                return lines[0], lines[1], lines[2]  # api_id, api_hash, phone
    return None, None, None

def save_credentials(api_id, api_hash, phone):
    with open(CREDENTIALS_FILE, "w") as f:
        f.write(f"{api_id}\n{api_hash}\n{phone}\n")

def list_channels():
    api_id, api_hash, phone = read_credentials()
    if not all([api_id, api_hash, phone]):
        api_id = int(input("Inserisci API ID: "))
        api_hash = input("Inserisci API Hash: ")
        phone = input("Inserisci il tuo numero di telefono: ")
        save_credentials(api_id, api_hash, phone)

    client = TelegramClient('session_id', int(api_id), api_hash)

    async def main():
        await client.start(phone)
        dialogs = await client.get_dialogs()
        print("\nLista dei tuoi canali e supergruppi:")
        for dialog in dialogs:
            if dialog.is_channel:
                print(f"Titolo: {dialog.title} | ID: {dialog.id} | Username: {dialog.entity.username}")

    asyncio.run(main())

def generate_bot():
    api_id, api_hash, phone_number = read_credentials()
    if not all([api_id, api_hash, phone_number]):
        api_id = int(input("Inserisci API ID: "))
        api_hash = input("Inserisci API Hash: ")
        phone_number = input("Inserisci numero di telefono: ")
        save_credentials(api_id, api_hash, phone_number)

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

    # Correzione variabili shell
    template_sh = """#!/bin/bash
PYTHON=$(which python3)
BOT_SCRIPT="{py_file}"
LOG_FILE="${{BOT_SCRIPT}}.log"

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

    source_id = int(input("Inserisci ID del canale sorgente: "))
    dest_id = int(input("Inserisci ID del canale destinazione: "))
    kw_input = input("Inserisci parole chiave separate da virgola (o lascia vuoto per tutte): ")
    keywords = [k.strip() for k in kw_input.split(",") if k.strip()] if kw_input else []

    py_filename = f"forwarder_{source_id}_{dest_id}.py"
    with open(py_filename, "w", encoding="utf-8") as f:
        f.write(template_py.format(api_id=api_id, api_hash=api_hash, phone_number=phone_number,
                                   source_id=source_id, dest_id=dest_id, keywords=keywords))

    sh_filename = f"start_forwarder_{source_id}_{dest_id}.sh"
    with open(sh_filename, "w", encoding="utf-8") as f:
        f.write(template_sh.format(py_file=py_filename))

    os.chmod(sh_filename, 0o755)

    print(f"\n✅ File generati:")
    print(f" - Script Python: {py_filename}")
    print(f" - Script avvio background: {sh_filename}")
    print(f"Avvia il bot con: bash {sh_filename}")

if __name__ == "__main__":
    print("Scegli un'opzione:")
    print("1. Mostra lista canali e ID")
    print("2. Genera bot e script di avvio")

    choice = input("Inserisci scelta (1 o 2): ")
    if choice == "1":
        list_channels()
    elif choice == "2":
        generate_bot()
    else:
        print("Scelta non valida")
