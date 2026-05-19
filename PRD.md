# Product Requirements Document (PRD)

## [camarilla / sistema de orden de articulos del hogar]

| Campo | Valor |
|-------|-------|
| **Versión** | 1.0 |
| **Fecha** | 2026-05-18 |
| **Estado** | Vigente |
| **Autor** | Nahuel Palacio |

---

## 1. Contexto y Objetivos

> **proyecto nuevo**
> estamos empezando este proyecto que se basa en que un pequeño modelo de IA pueda responder en base a preguntas sencillas del tipo"¿Donde esta mi destornillador?" y que el modelo mediante un archivo .MD sepa que el destornillador esta por ejemplo en el cajon numero 3 de la estanteria.
### 1.1 Problema Actual
No se logran encontrar cosas que se guardaron hace mucho tiempo y se pierde demasiado tiempo buscando incluso hay que veces que no se pueden encontrar por no saber donde estan.
### 1.2 Objetivo General
el impacto esperado es que mediante una ventana de chat simple y preguntas sencillas se puedan encontrar el objeto deseado.
### 1.3 Alcance por Fases
Si el proyecto es grande, dividilo en iteraciones manejables. ¡No construyas todo de una, buscá feedback temprano!

| Fase | Módulo / Feature | Descripción | Prioridad |
|------|------------------|-------------|-----------|
| **1** | MVP | generacion de una plantilla para que el usuario pueda llenar a mano de donde estan las cosas en su lugar | **ALTA** |
| **2** | [Módulo 1] | Generar el canal por el cual el usuario va a hablar con la IA, necesitamos que sea a travez de telegram | **ALTA** |
| **3** | [Módulo 2] | Conseguir que el usuario pueda decirle al modelo que cambio algo de lugar y que quede guardado en el MD | **ALTA** |

---

## 2. Fase inicial: MVP

### 2.1 Descripción
el usuario final solo hablara por el chat de telegram para poder buscar su objeto perdido
### 2.2 Actores

| Actor | Rol / Responsabilidad |
|-------|-----------------------|
| **usuario** | solo habla con el modelo por telegram y los permisos son los minimos que necesita. |

### 2.3 Flujo Principal (User Journeys)
El usuario entra a telegram, elige el bot y le habla
### 2.4 Requisitos Funcionales (RF)

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-1.1 | El sistema debe permitir ver y modificar el md con el orden de los objetos | ALTA |

