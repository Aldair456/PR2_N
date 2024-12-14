from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
from Funciones.condicionales import condicionalesLetras
from Funciones.normalizacionCords import obtenerAngulos

app = Flask(__name__)

lectura_actual = 0
cap = None
camera_running = False

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_drawing_styles = mp.solutions.drawing_styles

# Inicializamos el objeto Hands una sola vez
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.75
)

def start_camera():
    global cap, camera_running
    if not camera_running:
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 720)
        camera_running = True

def stop_camera():
    global cap, camera_running
    if camera_running:
        if cap is not None:
            cap.release()
            cap = None
        camera_running = False

def gen_frames():
    global lectura_actual, cap, camera_running
    while camera_running and cap is not None and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        height, width, _ = frame.shape
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(frame_rgb)
        if results.multi_hand_landmarks is not None:
            angulosid = obtenerAngulos(results, width, height)[0]

            dedos = []
            # Pulgar externo
            if angulosid[5] > 125:
                dedos.append(1)
            else:
                dedos.append(0)

            # Pulgar interno
            if angulosid[4] > 150:
                dedos.append(1)
            else:
                dedos.append(0)

            # Cuatro dedos restantes
            for id in range(0, 4):
                if angulosid[id] > 90:
                    dedos.append(1)
                else:
                    dedos.append(0)

            condicionalesLetras(dedos, frame)

            pinky = obtenerAngulos(results, width, height)[1]
            pinkY = pinky[1] + pinky[0]
            resta = pinkY - lectura_actual
            lectura_actual = pinkY
            print(abs(resta), pinkY, lectura_actual)

            if dedos == [0, 0, 1, 0, 0, 0]:
                if abs(resta) > 30:
                    print("jota en movimiento")
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.rectangle(frame, (0, 0), (100, 100), (255, 255, 255), -1)
                    cv2.putText(frame, 'J', (20, 80), font, 3, (0, 0, 0), 2, cv2.LINE_AA)

            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/conocenos.html')
def conocenos():
    return render_template('conocenos.html')

@app.route('/frases.html')
def frases():
    return render_template('frases.html')

@app.route('/video_feed')
def video_feed():
    if camera_running:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return jsonify(status="Camera not running"), 400

@app.route('/start_camera', methods=['POST'])
def start_camera_route():
    start_camera()
    return jsonify(status="Camera started")

@app.route('/stop_camera', methods=['POST'])
def stop_camera_route():
    stop_camera()
    return jsonify(status="Camera stopped")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
