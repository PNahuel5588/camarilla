# Camarilla — Guía para Humanos

## Probar el proyecto localmente

### Setup

```bash
# Clonar e instalar
git clone <repo-url> camarilla && cd camarilla
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Probar que funciona

```bash
# Entry point (no hace nada en Fase 1, pero no debe fallar)
python -m camarilla

# Correr los tests
pytest -v

# Con coverage
pytest --cov=camarilla -v
```

### Probar inventario.py manualmente

```python
from camarilla.inventario import leer_inventario, escribir_inventario
from camarilla.config import INVENTARIO_PATH, BACKUPS_DIR

# Leer el inventario de ejemplo
data = leer_inventario()
print(data)
# {'Taller': {'Estantería': {'Cajón 1': ['Alicates', 'Destornillador Phillips'], '': ['Caja de herramientas', 'Tornillos varios']}, ...}}

# Modificar y guardar (se crea backup automático)
data["Taller"]["Estantería"]["Cajón 1"].append("Cinta métrica")
escribir_inventario(data)

# Verificar que se guardó
print(leer_inventario())

# Ver los backups creados
import os
print(os.listdir(BACKUPS_DIR))
```

### Formato de inventario.md

```
# Inventario del Hogar        ← título (se ignora en el data model)

## Taller                     ← habitación
### Estantería                ← mueble
- Caja de herramientas        ← item
- Tornillos varios
#### Cajón 1                  ← subdivisión (soporta cualquier profundidad)
- Alicates
- Destornillador Phillips
```

Reglas:
- `#` = título del documento
- `##` = habitación
- `###` = mueble
- `####` y más = subdivisiones (cajones, estantes, etc.)
- `- ` = item dentro del último header
- Codificación: UTF-8 siempre

---

## Deploy en Proxmox CT

### Estado actual (Fase 1)

En Fase 1 NO hay bot todavía. Solo tenés el módulo de lectura/escritura del inventario. El bot se implementa en Fase 2. Pero podés preparar el CT ahora.

### 1. Crear el CT en Proxmox

```bash
# En el host Proxmox, crear un CT Debian/Ubuntu
pct create 200 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname camarilla \
  --memory 1024 \
  --cores 2 \
  --storage local-lvm \
  --rootfs local-lvm:8 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --unprivileged 1

# Iniciar
pct start 200

# Entrar
pct enter 200
```

### 2. Instalar dependencias en el CT

```bash
# Dentro del CT
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git

# Clonar el repo
cd /opt
git clone <repo-url> camarilla
cd camarilla

# Crear venv e instalar
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Verificar
python -m camarilla
pytest -v
```

### 3. Instalar Ollama

```bash
# Dentro del CT
curl -fsSL https://ollama.com/install.sh | sh

# Descargar el modelo (qwen2:1.5b — recomendado, liviano y rápido)
ollama pull qwen2:1.5b

# Verificar que responde
ollama run qwen2:1.5b "hi"
```

Requisitos de RAM por modelo:

| Modelo | RAM mínima | Disco | Velocidad |
|--------|-----------|-------|-----------|
| `qwen2:1.5b` | ~2 GB | ~1 GB | Rápido (~2-5s) |
| `phi3:3.8b` | ~4 GB | ~2.5 GB | Medio (~5-15s) |
| `llama3:8b` | ~8 GB | ~5 GB | Lento (~15-45s) |

Para cambiar el modelo: setear `OLLAMA_MODEL=phi3` en el environment.

### 4. Configurar el bot de Telegram (Fase 2)

```bash
# 1. Hablar con @BotFather en Telegram
# 2. /newbot → nombre: "Camarilla" → username: "camarilla_tu_bot"
# 3. Guardar el token que te da
# 4. Obtener tu user_id: hablar con @userinfobot

# Configurar como variable de entorno en el CT
echo 'export TELEGRAM_BOT_TOKEN="tu-token-aqui"' >> ~/.bashrc
echo 'export TELEGRAM_USER_ID="tu-user-id-aqui"' >> ~/.bashrc
source ~/.bashrc
```

### 5. Correr el bot como servicio (Fase 2+)

```bash
# Crear systemd service
cat > /etc/systemd/system/camarilla.service << 'EOF'
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
Environment=TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
Environment=TELEGRAM_USER_ID=${TELEGRAM_USER_ID}
Environment=OLLAMA_MODEL=qwen2:1.5b

[Install]
WantedBy=multi-user.target
EOF

# Habilitar y arrancar
systemctl daemon-reload
systemctl enable camarilla
systemctl start camarilla

# Ver logs
journalctl -u camarilla -f
```

---

## Checklist de Fases

| Fase | Estado | Qué hace |
|------|--------|----------|
| 1 | ✅ Completa | Estructura + lectura/escritura segura de inventario.md |
| 2 | ✅ Completa | Bot de Telegram con aiogram |
| 3 | ✅ Completa | Integración con Ollama (IA local) |
| 4 | 🔲 Pendiente | Modificación del inventario por chat |
