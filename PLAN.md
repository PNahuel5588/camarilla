# Plan de Proyecto: Camarilla (Sistema de Orden Hogareño)

## 1. Visión General
"Camarilla" es un bot de Telegram diseñado para gestionar el inventario del hogar. Su función principal es permitir al usuario encontrar objetos perdidos y actualizar la ubicación de los mismos mediante lenguaje natural. 
El sistema es 100% local, enfocado en la privacidad, y utiliza un archivo Markdown como base de datos ligera.

## 2. Arquitectura y Stack Tecnológico
- **Entorno de Ejecución:** Contenedor (CT) en Proxmox (Linux).
- **Lenguaje Base:** Python 3.11+.
- **Interfaz de Usuario:** Telegram Bot API (librería recomendada: `python-telegram-bot` o `aiogram`).
- **Cerebro (IA):** Modelo local corriendo a través de **Ollama** (ej. Llama 3 8B, Phi-3 o Qwen2). El bot se comunicará con Ollama a través de su API REST local (`http://localhost:11434`).
- **Base de Datos:** Archivo local de texto plano (`inventario.md`).

## 3. Lógica de Funcionamiento (Core Loop)
1. **Recepción:** El usuario envía un mensaje por Telegram (ej. "¿Dónde está el destornillador?" o "Guardé la cinta en el cajón 2").
2. **Lectura de Contexto:** Python lee el archivo `inventario.md` actual en memoria.
3. **Procesamiento de IA:** Python envía un prompt al modelo local de Ollama. Este prompt incluye:
   - Las instrucciones del sistema (Rol de la IA).
   - El contenido actual de `inventario.md`.
   - El mensaje del usuario.
4. **Enrutamiento de Acción:** 
   - *Si es una consulta:* La IA responde dónde está el objeto basándose en el `.md`.
   - *Si es una actualización:* La IA debe devolver un formato estructurado (ej. JSON) indicando qué se agregó/movió y a dónde, para que Python modifique y guarde el `inventario.md`.
5. **Respuesta:** El bot envía la confirmación o la respuesta por Telegram al usuario.

## 4. Fases de Desarrollo (Roadmap)

### Fase 1: MVP - Estructura y Base de Datos (Actual)
- [ ] Crear la estructura de carpetas del proyecto.
- [ ] Definir el formato del `inventario.md` (ej. una tabla o listas anidadas por habitación/mueble).
- [ ] Crear funciones en Python para leer y escribir de forma segura en `inventario.md`.

### Fase 2: Conexión con Telegram Bot
- [ ] Registrar el bot en BotFather (Telegram) y obtener el Token.
- [ ] Configurar el script de Python para escuchar mensajes entrantes.
- [ ] Implementar un control de acceso (Hardcodear el `user_id` del dueño para que nadie más pueda hablar con el bot).

### Fase 3: Integración de Inteligencia Artificial (Ollama)
- [ ] Instalar Ollama en el CT de Proxmox y descargar el modelo elegido (`ollama run phi3`).
- [ ] Conectar el bot de Python con la API local de Ollama (usando `requests` o la librería oficial de `ollama` para Python).
- [ ] Diseñar el "System Prompt" para consultas de lectura.

### Fase 4: Modificación del Inventario por Chat
- [ ] Implementar extracción de entidades (Tool Calling / Structured Output) en Ollama para detectar cuando el usuario quiere guardar algo nuevo.
- [ ] Desarrollar la lógica en Python que actualiza la línea correspondiente en `inventario.md` sin romper el formato.

## 5. Reglas de Código (Guía para la IA)
- **Privacidad primero:** No se deben usar APIs externas para el procesamiento de lenguaje. Todo debe apuntar a la instancia local de Ollama.
- **Simplicidad:** Mantener el manejo del archivo `.md` lo más robusto pero simple posible. Evitar bases de datos relacionales; el archivo `.md` es la única fuente de verdad.
- **Manejo de Errores:** Si el archivo `.md` se corrompe o está bloqueado, el bot debe avisar por Telegram y mantener un backup automático de la versión anterior antes de cada escritura.
- **Seguridad en Telegram:** El bot debe rechazar silenciosamente cualquier mensaje que provenga de un `chat_id` no autorizado.
