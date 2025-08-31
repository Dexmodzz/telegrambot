Installare Python 3 e pip (se non già presenti)
sudo apt update
sudo apt install python3 python3-pip -y

4️⃣ Avviare il setup per generare il bot
python3 setup_forwarder.py


Ti verranno chiesti:

API ID

API Hash

Numero di telefono Telegram

ID canale sorgente

ID canale destinazione

Parole chiave (opzionale)

Lo script genererà automaticamente:

forwarder_<sourceID>_<destID>.py

start_forwarder_<sourceID>_<destID>.sh

5️⃣ Avviare il bot in background
bash start_forwarder_<sourceID>_<destID>.sh


Il bot rimane attivo anche se chiudi la sessione SSH.

I log vengono salvati in forwarder_<sourceID>_<destID>.py.log.

6️⃣ Controllare lo stato del bot

Verifica i processi Python attivi:

ps aux | grep python


Se vuoi interrompere il bot:

kill <PID>


dove <PID> è l’ID del processo Python.

7️⃣ Aggiornare o modificare il bot

Se vuoi cambiare canali o parole chiave, modifica il file forwarder_<sourceID>_<destID>.py e poi riavvia il bot:

bash start_forwarder_<sourceID>_<destID>.sh

8️⃣ Avvio automatico al riavvio della VPS (opzionale)

Puoi creare un servizio systemd così il bot parte automaticamente:

sudo nano /etc/systemd/system/telegram_forwarder.service


Contenuto esempio:

[Unit]
Description=Telegram Forwarder Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/utente/telegram_forwarder_package
ExecStart=/usr/bin/python3 /home/utente/telegram_forwarder_package/forwarder_<sourceID>_<destID>.py
Restart=always
RestartSec=5
User=utente

[Install]
WantedBy=multi-user.target


Abilita e avvia il servizio:

sudo systemctl daemon-reload
sudo systemctl enable telegram_forwarder
sudo systemctl start telegram_forwarder
sudo systemctl status telegram_forwarder


Con questo flusso, non serve creare virtual environment, non serve pipx, e puoi usare pip3 globale grazie allo script .sh che gestisce l’installazione di Telethon.