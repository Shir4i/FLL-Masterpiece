import cv2
import mediapipe as mp
import math
from pygame import mixer

class Circle:
    def __init__(self, x, y, checked, note, played = False):
        self.x = x
        self.y = y
        self.checked = checked
        self.note = note
        self.played = played

mixer.init()

# AQUI VC ADICIONA OS ARQUIVOS DE SOM   
nota_c = mixer.Sound('C.wav')
nota_d = mixer.Sound('D.wav')
nota_e = mixer.Sound('E.wav')
nota_g = mixer.Sound('G.wav')

# AQUI VC ADICIONA PONTOS
circles = [Circle(50, 50, False, nota_), 
           Circle(150, 50, False, nota_), 
           Circle(250, 50, False, nota_), 
           Circle(350, 50, False, nota_), 
           Circle(450, 50, False, nota_), 
           Circle(590, 50, False, nota_), 
           Circle(50, 150, False, nota_),
           Circle(150, 150, False, nota_    ),]

lastPos = -1
changed = False
line = 0
playing = -1

cap = cv2.VideoCapture(0)
execs = 0
dist_total = 0
hand_size_total = 0

# res: 480 x 640

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=.25,
    model_complexity = 0)
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
                    if abs(index_finger_tip.x * 640 - circle.x) <= 35 and abs(index_finger_tip.y * 480 - circle.y) <= 35:
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
                circle.note.play()
                circle.played = True

        else:
            cv2.circle(img, (circle.x, circle.y), 10, (255, 0, 0), 1)

    cv2.imshow("Image", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    line+=5

    if line >= 640:
        for circle in circles:
            circle.played = False
        line = 0

    cv2.waitKey(1)