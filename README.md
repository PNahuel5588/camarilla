# Camarilla: Sistema de Orden de Artículos del Hogar

## 1. Onboarding (Introducción para Seres Humanos)
¡Bienvenido/a a Camarilla! 
¿Alguna vez guardaste un destornillador, un cable o un documento importante y meses después no tenías idea de dónde estaba? Camarilla resuelve exactamente eso. 

Es un asistente de inventario hogareño que funciona a través de un chat de Telegram. Detrás de escena, utiliza Inteligencia Artificial (completamente local y privada) para leer y actualizar un archivo de texto simple (`inventario.md`). Solo tenés que enviarle un mensaje diciendo: *"Guardé la cinta aisladora en el tercer cajón del taller"* y el sistema se encarga de recordarlo para cuando, meses después, le preguntes *"¿Dónde está la cinta aisladora?"*.

---

## 2. Guía para el Usuario Operador

Esta sección está destinada al administrador encargado de poner el sistema en marcha, asegurar el entorno y mantenerlo actualizado dentro de un contenedor (CT) de Proxmox.

### A. Despliegue (Deployment) en Ambiente Nuevo

**Requisitos Previos del CT (Proxmox):**
* SO: Linux (Debian/Ubuntu recomendado).
* Instalados: `python3.11+`, `git`, `pip`, `venv`.
* [Ollama](https://ollama.com/) instalado y corriendo como servicio.

**Pasos de Instalación:**
1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repo> /opt/camarilla
   cd /opt/camarilla
