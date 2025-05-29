# Proyecto IoT robotica

## pasos para funcionamiento

Guía Completa para Configurar el Entorno Virtual y Ejecutar el Programa
1. Crear un entorno virtual (venv)
En Windows:
Abre CMD o PowerShell y ejecuta
```
python --version
```
2 La version de python debe ser Python 3.11.x porque las versiones 3.12 en adelante no son compatibles

3 Descarga https://github.com/marytc/record_and_play.git y descomprime
4 Luego abre Powershell y arrastra la carpeta descomprimida
```
cd [carpeta comprimida]
```
5. Ya estas dentro de la carpeta en powershell ejecuta

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

```

# Para hacer correr el codigo python

```
python record_and_play.py
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