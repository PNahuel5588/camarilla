# Camarilla <img src="./asset.png" width="50" alt="Captura del proyecto">

Asistente de inventario hogareño por Telegram con IA local. Privado, simple, 100% gratuito.

¿Guardaste algo y no sabés dónde está? Preguntale a Camarilla por Telegram y te responde al instante basándose en tu inventario.

## Cómo funciona

```
Telegram ──→ Bot (aiogram) ──→ Ollama (IA local) ──→ inventario.md
                │                      │
                │  "¿Dónde está el     │  Lee tu inventario
                │   destornillador?"   │  y genera la respuesta
                │                      │
                └──────────────────────┘
```

- **inventario.md** — única fuente de verdad, formato Markdown editable
- **Ollama** — IA 100% local, sin APIs externas, sin costo
- **Telegram** — interfaz simple, preguntas en lenguaje natural
- **Backups** — automáticos antes de cada escritura (últimos 10)

## Comandos del bot

| Comando | Qué hace |
|---------|----------|
| `/start` | Mensaje de bienvenida |
| `/help` | Lista de comandos disponibles |
| `/inventario` | Muestra el inventario completo |
| Cualquier texto | Pregunta a la IA sobre tu inventario |

## Stack

| Componente | Tecnología |
|------------|-----------|
| Lenguaje | Python 3.11+ |
| Bot | aiogram v3 |
| IA | Ollama (qwen2:1.5b) |
| Base de datos | inventario.md (Markdown) |
| Deploy | Proxmox CT (Linux) |

## Estado del proyecto

| Fase | Estado | Qué hace |
|------|--------|----------|
| 1 | ✅ Completa | Estructura + lectura/escritura segura de inventario.md |
| 2 | ✅ Completa | Bot de Telegram con aiogram |
| 3 | ✅ Completa | Integración con Ollama (IA local) |
| 4 | 🔲 Pendiente | Modificación del inventario por chat |

## Desarrollo local

```bash
git clone https://github.com/PNahuel5588/camarilla.git && cd camarilla
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

## Deploy en Proxmox CT

### 1. Crear el CT

```bash
# En el host Proxmox
pct create 200 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname camarilla \
  --memory 4096 \
  --cores 2 \
  --storage local-lvm \
  --rootfs local-lvm:8 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --unprivileged 1

pct start 200
pct enter 200
```

### 2. Instalar base

```bash
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git
```

### 3. Instalar el proyecto

```bash
cd /opt
git clone https://github.com/PNahuel5588/camarilla.git
cd camarilla
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v  # verificar que pasa los 33 tests
```

### 4. Instalar Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2:1.5b
ollama run qwen2:1.5b "hola"  # verificar
```

Requisitos de RAM por modelo:

| Modelo | RAM mínima | Disco | Velocidad |
|--------|-----------|-------|-----------|
| `qwen2:1.5b` | ~2 GB | ~1 GB | Rápido (~2-5s) |
| `phi3:3.8b` | ~4 GB | ~2.5 GB | Medio (~5-15s) |
| `llama3:8b` | ~8 GB | ~5 GB | Lento (~15-45s) |

Para cambiar el modelo: `OLLAMA_MODEL=phi3` en el environment.

### 5. Configurar Telegram

1. Hablar con `@BotFather` → `/newbot` → nombre "Camarilla" → obtener **token**
2. Hablar con `@userinfobot` → obtener tu **user_id**
3. Pedirle el user_id a cada persona que quieras que use el bot

### 6. Crear el servicio

```bash
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
Environment=TELEGRAM_BOT_TOKEN=tu-token-aqui
Environment=TELEGRAM_USER_IDS=123456,789012
Environment=OLLAMA_MODEL=qwen2:1.5b

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable camarilla
systemctl start camarilla
journalctl -u camarilla -f  # verificar que arrancó
```

### 7. Probar

- Mandar `/start` → responde "Welcome to Camarilla!"
- Mandar `/inventario` → muestra el inventario de ejemplo
- Mandar "¿Dónde está el destornillador?" → Ollama responde

### 8. Agregar tu inventario real

Editar `/opt/camarilla/inventario.md` con tus cosas:

```markdown
# Inventario del Hogar

## Taller
### Estantería
- Caja de herramientas
- Tornillos varios
#### Cajón 1
- Alicates
- Destornillador Phillips
```

Formato: `##` = habitación, `###` = mueble, `####`+ = subdivisiones, `- ` = items.

### Actualizar el bot

```bash
cd /opt/camarilla
git pull
source .venv/bin/activate
pip install -e ".[dev]"
systemctl restart camarilla
```

### Agregar más usuarios

Editar `/etc/systemd/system/camarilla.service` y agregar los user_ids separados por coma:

```
Environment=TELEGRAM_USER_IDS=123456,789012,nuevo_id
```

```bash
systemctl daemon-reload
systemctl restart camarilla
```

### Cambiar el modelo de IA

Editar el `Environment=OLLAMA_MODEL=` en el service, descargar el modelo, y restart:

```bash
ollama pull phi3
# Editar service: OLLAMA_MODEL=phi3
systemctl daemon-reload
systemctl restart camarilla
```

## Licencia

Privado — uso personal.
