import cv2
import mediapipe as mp
import numpy as np
import json
import time
import pygame
from pygame import mixer
import os

# Inicializacion de librerías
pygame.init()
mixer.init()

# Configuracion de MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Variables globales
recording = False
playing = False
recorded_data = []
start_time = 0
last_frame_time = 0

# Configuracion de ventanas
cv2.namedWindow("Motion Capture", cv2.WINDOW_NORMAL)
cv2.namedWindow("Playback", cv2.WINDOW_NORMAL)

# Crear carpeta para grabaciones
os.makedirs('recordings', exist_ok=True)

def save_recording(data):
    """Guarda la grabación en un archivo JSON"""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"recordings/recording_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Grabación guardada como {filename}")
    return filename

def load_recording(filename):
    """Carga una grabacion desde archivo"""
    with open(filename, 'r') as f:
        return json.load(f)

def play_sound(action):
    """Reproduce sonidos de feedback"""
    try:
        sounds = {
            "start": "start.wav",
            "stop": "stop.wav", 
            "play": "play.wav"
        }
        if action in sounds and os.path.exists(sounds[action]):
            mixer.Sound(sounds[action]).play()
    except Exception as e:
        print(f"Error con sonidos: {e}")

def draw_landmarks(image, landmarks, connections, color, thickness):
    """Dibuja landmarks y conexiones en una imagen"""
    if landmarks is None:
        return
    
    landmarks_array = np.array([[lm.x, lm.y] for lm in landmarks.landmark])
    
    for connection in connections:
        start_idx, end_idx = connection
        if 0 <= start_idx < len(landmarks_array) and 0 <= end_idx < len(landmarks_array):
            start_point = tuple(np.multiply(landmarks_array[start_idx], [image.shape[1], image.shape[0]]).astype(int))
            end_point = tuple(np.multiply(landmarks_array[end_idx], [image.shape[1], image.shape[0]]).astype(int))
            cv2.line(image, start_point, end_point, color, thickness)
            cv2.circle(image, start_point, thickness, (255, 255, 255), -1)

def main():
    global recording, playing, recorded_data, start_time, last_frame_time
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Error al abrir la cámara")
        return

    with mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as holistic:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar frame")
                break

            # Procesamiento del frame
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(frame_rgb)

            # Dibujar landmarks
            draw_landmarks(
                frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                (128, 0, 255), 2)

            # Mostrar estado
            status_text = "Grabando..." if recording else "Listo"
            cv2.putText(frame, status_text, (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Motion Capture", frame)

            # Manejo de teclas
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('r'):  # Iniciar/detener grabación
                if not recording:
                    recording = True
                    recorded_data = []
                    start_time = time.time()
                    last_frame_time = start_time
                    play_sound("start")
                    print("Iniciando grabación...")
                else:
                    recording = False
                    if recorded_data:
                        save_recording(recorded_data)
                    play_sound("stop")
                    print("Grabación detenida")

            elif key == ord('p') and not recording:  # Reproducir
                if recorded_data:
                    play_recording(recorded_data)
                else:
                    print("No hay datos para reproducir")

            elif key == 27:  # Salir
                break

            # Grabación de datos
            if recording and results.pose_landmarks:
                current_time = time.time()
                frame_time = current_time - last_frame_time
                last_frame_time = current_time
                
                pose_data = []
                for landmark in results.pose_landmarks.landmark:
                    pose_data.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    })
                
                recorded_data.append({
                    'timestamp': current_time,
                    'frame_time': frame_time,
                    'pose_landmarks': pose_data
                })

    cap.release()
    cv2.destroyAllWindows()

def play_recording(recording_data):
    """Reproduce una grabación a velocidad real"""
    global playing
    
    playing = True
    play_sound("play")
    print(f"Reproduciendo grabación ({len(recording_data)} frames)...")
    
    playback_window = np.zeros((480, 640, 3), dtype=np.uint8)
    start_time = time.time()
    
    for i, frame_data in enumerate(recording_data):
        if not playing:
            break
            
        if not frame_data.get('pose_landmarks'):
            continue
            
        # Limpiar y dibujar frame
        playback_window.fill(0)
        landmarks = []
        
        for lm in frame_data['pose_landmarks']:
            landmarks.append([lm['x'], lm['y']])
        
        landmarks = np.array(landmarks)
        
        for connection in mp_holistic.POSE_CONNECTIONS:
            if connection[0] < len(landmarks) and connection[1] < len(landmarks):
                start_point = (int(landmarks[connection[0]][0] * 640), 
                              int(landmarks[connection[0]][1] * 480))
                end_point = (int(landmarks[connection[1]][0] * 640), 
                            int(landmarks[connection[1]][1] * 480))
                cv2.line(playback_window, start_point, end_point, (128, 0, 255), 2)
                cv2.circle(playback_window, start_point, 3, (255, 255, 255), -1)
        
        # Mostrar información
        cv2.putText(playback_window, f"Frame: {i+1}/{len(recording_data)}", 
                   (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        
        cv2.imshow("Playback", playback_window)
        
        # Control de velocidad
        if i < len(recording_data) - 1:
            target_delay = recording_data[i+1]['frame_time']
            elapsed = time.time() - start_time
            remaining_delay = max(0, target_delay - elapsed)
            time.sleep(remaining_delay)
            start_time = time.time()
        
        if cv2.waitKey(1) & 0xFF == 27:  # ESC para cancelar
            playing = False
            break
    
    playing = False
    print("Reproducción completada")

if __name__ == "__main__":
    main()