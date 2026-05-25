# Camarilla — Guía Operativa

## Probar localmente

```bash
git clone https://github.com/PNahuel5588/camarilla.git && cd camarilla
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

### Probar inventario.py manualmente

```python
from camarilla.inventario import leer_inventario, escribir_inventario
from camarilla.config import INVENTARIO_PATH, BACKUPS_DIR

data = leer_inventario()
print(data)

data["Taller"]["Estantería"]["Cajón 1"].append("Cinta métrica")
escribir_inventario(data)
```

### Formato de inventario.md

```
# Inventario del Hogar        ← título (se ignora)
## Taller                     ← habitación
### Estantería                ← mueble
- Caja de herramientas        ← item
#### Cajón 1                  ← subdivisión (cualquier profundidad)
- Alicates
```

---

## Deploy en Proxmox CT — TO-DO

### Proxmox Host
- [ ] Crear CT Debian 12 (4GB RAM, 8GB disco, 2 cores, DHCP)
- [ ] Iniciar CT y entrar (`pct enter`)

### Dentro del CT — Base
- [ ] `apt update && apt upgrade -y`
- [ ] `apt install -y python3 python3-pip python3-venv git`

### Dentro del CT — Proyecto
- [ ] `cd /opt && git clone https://github.com/PNahuel5588/camarilla.git`
- [ ] `cd camarilla && python3 -m venv .venv`
- [ ] `source .venv/bin/activate && pip install -e ".[dev]"`
- [ ] `pytest -v` → verificar que pasan los 33 tests

### Dentro del CT — Ollama
- [ ] `curl -fsSL https://ollama.com/install.sh | sh`
- [ ] `ollama pull qwen2:1.5b`
- [ ] Verificar: `ollama run qwen2:1.5b "hola"` → responde algo

### Telegram
- [ ] Hablar con `@BotFather` → `/newbot` → nombre "Camarilla" → obtener **token**
- [ ] Hablar con `@userinfobot` → obtener tu **user_id**
- [ ] Pedirle el user_id a cada persona que quieras que use el bot

### Dentro del CT — Service
- [ ] Crear `/etc/systemd/system/camarilla.service`:

```
[Unit]
Description=Camarilla Home Inventory Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/camarilla
ExecStart=/opt/camarilla/.venv/bin/python -m camarilla
Restart=always
RestartSec=5
Environment=TELEGRAM_BOT_TOKEN=tu-token-aqui
Environment=TELEGRAM_USER_IDS=123456,789012
Environment=OLLAMA_MODEL=qwen2:1.5b

[Install]
WantedBy=multi-user.target
```

- [ ] `systemctl daemon-reload`
- [ ] `systemctl enable camarilla`
- [ ] `systemctl start camarilla`
- [ ] `journalctl -u camarilla -f` → verificar que arrancó sin errores

### Post-deploy
- [ ] Probar en Telegram: `/start` → responde "Welcome to Camarilla!"
- [ ] Probar: `/inventario` → muestra el inventario de ejemplo
- [ ] Probar: "¿Dónde está el destornillador?" → Ollama responde
- [ ] Editar `inventario.md` con tus cosas reales
- [ ] Probar de nuevo con tu inventario real

---

## Operaciones comunes

### Actualizar el bot
```bash
cd /opt/camarilla && git pull
source .venv/bin/activate && pip install -e ".[dev]"
systemctl restart camarilla
```

### Agregar un usuario
Editar `TELEGRAM_USER_IDS` en el service, agregar el ID separado por coma, y restart:
```bash
systemctl daemon-reload && systemctl restart camarilla
```

### Cambiar modelo de IA
```bash
ollama pull phi3
# Editar service: OLLAMA_MODEL=phi3
systemctl daemon-reload && systemctl restart camarilla
```

### Ver logs
```bash
journalctl -u camarilla -f
```

---

## Estado del proyecto

| Fase | Estado | Qué hace |
|------|--------|----------|
| 1 | ✅ Completa | Estructura + lectura/escritura segura de inventario.md |
| 2 | ✅ Completa | Bot de Telegram con aiogram |
| 3 | ✅ Completa | Integración con Ollama (IA local) |
| 4 | 🔲 Pendiente | Modificación del inventario por chat |
