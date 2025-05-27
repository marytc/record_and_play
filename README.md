# Proyecto IoT robotica

## pasos para funcionamiento

Guía Completa para Configurar el Entorno Virtual y Ejecutar el Programa
1. Crear un entorno virtual (venv)

Un entorno virtual permite aislar las dependencias del proyecto para evitar conflictos con otros proyectos.
En Windows:
    Abre CMD o PowerShell en la carpeta del proyecto.

    Ejecuta:
    sh
    Crea y Activa el entorno virtual
```
python -m venv venv
venv\Scripts\activate
```
Instala las librerias
```
pip install -r requirements.txt
```

# Ejecucion del programa

```
python record_play.py
```

## Controles:

        R: Iniciar/detener grabación.

        P: Reproducir la última grabación.

        ESC: Salir del programa.

 Posibles problemas y soluciones

    Error con cv2.CAP_DSHOW (solo Windows):
    Si falla la cámara, cambia:
    python

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Por esto:
cap = cv2.VideoCapture(0)  # Elimina CAP_DSHOW

# Notas
Si ya se tiene entorno virtual en windows ingresa con
```
venv\Scripts\activate
```
para salir del entorno virtual
```
deactivate
```