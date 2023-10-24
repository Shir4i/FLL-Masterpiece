import cv2
import mediapipe as mp
import math
from pygame import mixer

class Circle:
    def __init__(self, x, y, checked, note, played=False):
        self.x = x
        self.y = y
        self.checked = checked
        self.note = note
        self.played = played

mixer.init()

# Carregue seus arquivos de áudio (substitua com seus próprios caminhos de arquivos)
audio_files = [
    'c1.wav',
    'd1.wav',
    'e1.wav',
    'g1.wav',
    "c2.wav",
    "d2.wav",
    "e2.wav",
    "g3.wav",
    "c3.wav",
    "d3.wav",
    "e3.wav"
]

# Crie uma lista de notas repetindo os arquivos de áudio
notes = [mixer.Sound(file) for file in audio_files]

# Define as linhas horizontais e as notas associadas a cada linha
lines_and_notes = [
    (1, notes[0]),  # C
    (2, notes[1]),  # D
    (3, notes[2]),  # E
    (4, notes[3]),  # G
    (5, notes[4]),  # C
    (6, notes[5]),  # D
    (7, notes[6]),  # E
    (8, notes[7]),  # G
    (9, notes[8]),  # C
    (10, notes[9]),  # D
    (11, notes[10]),  # E
]

circles = []
for row in range(11):
    for col in range(16):
        x = int((col + 1) * 640 // 17)  # Distribuição simétrica em largura
        y = int((row + 1) * 480 // 12)  # Distribuição simétrica em altura

        # Encontre a nota associada a esta linha horizontal
        note = None
        for line, audio_file in lines_and_notes:
            if row == line - 1:
                note = audio_file
                break

        circles.append(Circle(x, y, False, note))

lastPos = -1
changed = False
line = 0
playing = -1

cap = cv2.VideoCapture(0)
execs = 0
dist_total = 0
hand_size_total = 0

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.25,
    model_complexity=0)
mpDraw = mp.solutions.drawing_utils

while True:
    success, img = cap.read()
    img = cv2.flip(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 1)
    process = hands.process(img)

    if process.multi_hand_landmarks:
        index_finger_tip = process.multi_hand_landmarks[0].landmark[8]
        middle_finger_tip = process.multi_hand_landmarks[0].landmark[12]
        wrist = process.multi_hand_landmarks[0].landmark[0]
        middle_finger_mcp = process.multi_hand_landmarks[0].landmark[9]

        mpDraw.draw_landmarks(img, process.multi_hand_landmarks[0], mpHands.HAND_CONNECTIONS)

        dist = math.sqrt(math.pow(index_finger_tip.x - middle_finger_tip.x, 2) + math.pow(index_finger_tip.y - middle_finger_tip.y, 2))
        handSize = math.sqrt(math.pow(wrist.x - middle_finger_mcp.x, 2) + math.pow(wrist.y - middle_finger_mcp.y, 2))

        dist_total += dist
        hand_size_total += handSize

        execs += 1
        if execs >= 1:
            if dist_total / hand_size_total >= 1:
                for index, circle in enumerate(circles):
                    if abs(index_finger_tip.x * 640 - circle.x) <= 10 and abs(index_finger_tip.y * 480 - circle.y) <= 10:
                        if lastPos != index:
                            circle.checked = not circle.checked
                            lastPos = index

                        changed = True

                if not changed:
                    lastPos = -1

            else:
                lastPos = -1

            execs = 0
            dist_total = 0
            hand_size_total = 0

    cv2.line(img, (line, 0), (line, 480), (255, 255, 255), 2)

    for circle in circles:
        if circle.checked:
            cv2.circle(img, (circle.x, circle.y), 10, (255, 0, 0), -1)
            if abs(circle.x - line) <= 5 and not circle.played:
                circle.played = True
                circle.note.play()

        else:
            cv2.circle(img, (circle.x, circle.y), 10, (255, 0, 0), 1)

    cv2.imshow("Image", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    line += 5

    if line >= 640:
        for circle in circles:
            circle.played = False
        line = 0

    cv2.waitKey(1)