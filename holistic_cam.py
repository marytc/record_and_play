import cv2
import mediapipe as mp
import numpy as np
import json
import time
import pygame
from pygame import mixer
import os

# Inicializar pygame y mixer
pygame.init()
mixer.init()

# Configuración de MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Variables globales
recording = False
playing = False
recorded_data = []
start_time = 0
frame_count = 0

# Crear carpeta para guardar grabaciones si no existe
if not os.path.exists('recordings'):
    os.makedirs('recordings')

def save_recording(data):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"recordings/recording_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Grabación guardada como {filename}")
    return filename

def load_recording(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def play_sound(action):
    try:
        if action == "start":
            mixer.Sound('start.wav').play()
        elif action == "stop":
            mixer.Sound('stop.wav').play()
        elif action == "play":
            mixer.Sound('play.wav').play()
    except:
        print("Archivos de sonido no encontrados. Continuando sin audio.")

# Configurar la captura de video
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cv2.namedWindow("Motion Capture")
cv2.namedWindow("Playback")

with mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=1) as holistic:

    while True:
        # Captura y procesamiento del frame actual
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(frame_rgb)

        # Dibujar landmarks de postura
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(128, 0, 255), thickness=2, circle_radius=1),
                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2))

        frame = cv2.flip(frame, 1)
        cv2.imshow("Motion Capture", frame)

        # Grabación de movimientos
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('r'):  # Iniciar/Detener grabación
            if not recording:
                recording = True
                recorded_data = []
                start_time = time.time()
                frame_count = 0
                play_sound("start")
                print("Iniciando grabación...")
            else:
                recording = False
                if recorded_data:  # Solo guardar si hay datos
                    filename = save_recording(recorded_data)
                    play_sound("stop")
                print("Grabación detenida")

        elif key == ord('p') and not recording:  # Reproducir grabación
            if recorded_data:
                playing = True
                play_sound("play")
                print("Reproduciendo grabación...")
                
                # Crear una ventana de reproducción
                playback_window = np.zeros((480, 640, 3), dtype=np.uint8)
                
                for frame_data in recorded_data:
                    if not frame_data.get('pose_landmarks'):
                        continue
                        
                    playback_window.fill(0)  # Limpiar el frame
                    
                    # Convertir landmarks a array numpy
                    landmarks = []
                    for lm in frame_data['pose_landmarks']:
                        landmarks.append([lm['x'], lm['y'], lm['z']])
                    landmarks = np.array(landmarks)
                    
                    # Dibujar conexiones
                    for connection in mp_holistic.POSE_CONNECTIONS:
                        if connection[0] < len(landmarks) and connection[1] < len(landmarks):
                            start_point = (int(landmarks[connection[0]][0] * 640), 
                                          int(landmarks[connection[0]][1] * 480))
                            end_point = (int(landmarks[connection[1]][0] * 640), 
                                        int(landmarks[connection[1]][1] * 480))
                            cv2.line(playback_window, start_point, end_point, (128, 0, 255), 2)
                            cv2.circle(playback_window, start_point, 3, (255, 255, 255), -1)
                            cv2.circle(playback_window, end_point, 3, (255, 255, 255), -1)
                    
                    cv2.imshow("Playback", playback_window)
                    
                    if cv2.waitKey(30) & 0xFF == 27:  # ESC para salir durante reproducción
                        break
                
                playing = False
                print("Reproducción completada")
            else:
                print("No hay datos grabados para reproducir")

        elif key == 27:  # ESC para salir
            break

        # Guardar datos si estamos grabando
        if recording and results.pose_landmarks:
            frame_count += 1
            elapsed_time = time.time() - start_time     
            
            # Convertir landmarks a formato serializable
            pose_data = []
            for landmark in results.pose_landmarks.landmark:
                pose_data.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            
            recorded_data.append({
                'frame': frame_count,
                'time': elapsed_time,
                'pose_landmarks': pose_data
            })

cap.release()
cv2.destroyAllWindows()