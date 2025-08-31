import os
import asyncio
from telethon import TelegramClient, events
import subprocess

CREDENTIALS_FILE = "credentials.txt"

def read_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            if len(lines) == 3:
                return lines[0], lines[1], lines[2]
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

    bot_name = input("Scegli un nome per il bot (senza spazi): ").strip()
    if not bot_name:
        bot_name = "forwarder_bot"

    template_py = """
import asyncio
from telethon import TelegramClient, events
import os
import sys

CREDENTIALS_FILE = "credentials.txt"

with open(CREDENTIALS_FILE, "r") as f:
    lines = [line.strip() for line in f.readlines()]
    api_id = int(lines[0])
    api_hash = lines[1]
    phone_number = lines[2]

session_file = "session_" + phone_number + ".session"
if not os.path.exists(session_file):
    print("❌ Sessione non trovata: " + session_file)
    print("   Avvia il bot una volta in modalità interattiva per generare la sessione.")
    sys.exit(1)

source_chat_id = {source_id}
destination_channel_id = {dest_id}
keywords = {keywords}

client = TelegramClient('session_' + phone_number, api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat_id))
async def handler(event):
    text = event.message.message.lower()
    if keywords:
        if event.message.text and any(k.lower() in text for k in keywords):
            await client.send_message(destination_channel_id, event.message.text)
    else:
        await client.send_message(destination_channel_id, event.message.text)

async def heartbeat():
    while True:
        print("💓 Bot attivo...")
        await asyncio.sleep(60)

print("🔍 Avvio del bot...")
client.loop.create_task(heartbeat())
client.start(phone=phone_number)
print("✅ Bot connesso correttamente a Telegram e in esecuzione...")
client.run_until_disconnected()
"""

    source_id = int(input("Inserisci ID del canale sorgente: "))
    dest_id = int(input("Inserisci ID del canale destinazione: "))
    kw_input = input("Inserisci parole chiave separate da virgola (o lascia vuoto per tutte): ")
    keywords = [k.strip() for k in kw_input.split(",") if k.strip()] if kw_input else []

    py_filename = f"{bot_name}.py"
    log_filename = f"{bot_name}.log"
    sh_filename = f"start_{bot_name}.sh"

    # Scrivi script Python del bot
    with open(py_filename, "w", encoding="utf-8") as f:
        f.write(template_py.format(api_id=api_id, api_hash=api_hash, phone_number=phone_number,
                                   source_id=source_id, dest_id=dest_id, keywords=keywords))

    # Genera lo script di avvio in background
    template_sh = f"""#!/bin/bash
PYTHON=$(which python3)
BOT_SCRIPT="{py_filename}"
LOG_FILE="{log_filename}"

echo "Verifica installazione Telethon..."
$PYTHON -m pip show telethon > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Telethon non trovato, installo..."
    $PYTHON -m pip install --break-system-packages --upgrade pip
    $PYTHON -m pip install telethon --break-system-packages
fi

echo "Avvio del bot in background..."
nohup $PYTHON -u "$BOT_SCRIPT" > "$LOG_FILE" 2>&1 &
echo "Bot avviato. Log in $LOG_FILE"
"""

    with open(sh_filename, "w", encoding="utf-8") as f:
        f.write(template_sh)

    os.chmod(sh_filename, 0o755)

    print(f"\n✅ File generati:")
    print(f" - Script Python: {py_filename}")
    print(f" - Script avvio background: {sh_filename}")
    print(f" - Log file: {log_filename}")
    print(f"Avvia il bot con: bash {sh_filename}")

def list_active_bots():
    print("\n🔍 Bot Python attivi:")
    try:
        result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True)
        lines = result.stdout.splitlines()
        bots = []
        for line in lines:
            if '.py' in line:
                print(line)
                bots.append(line)
        if not bots:
            print("Nessun bot attivo trovato.")
            return

        kill_option = input("\nVuoi terminare un bot attivo? (s/n): ").lower()
        if kill_option == 's':
            bot_name = input("Scrivi il nome dello script del bot da terminare (es: smartinvestorclub.py): ").strip()
            for line in bots:
                if bot_name in line:
                    pid = int(line.split()[1])
                    os.kill(pid, 9)
                    print(f"Bot {bot_name} terminato (PID {pid})")
                    break
            else:
                print("Nessun bot trovato con quel nome.")
    except Exception as e:
        print(f"Errore durante la ricerca dei bot attivi: {e}")

if __name__ == "__main__":
    print("Scegli un'opzione:")
    print("1. Mostra lista canali e ID")
    print("2. Genera bot e script di avvio")
    print("3. Mostra bot attivi e termina uno")

    choice = input("Inserisci scelta (1, 2 o 3): ")
    if choice == "1":
        list_channels()
    elif choice == "2":
        generate_bot()
    elif choice == "3":
        list_active_bots()
    else:
        print("Scelta non valida")

