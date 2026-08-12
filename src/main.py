import cv2
import pygame

from gestures.detector import GestureDetector
from tracking.hand_tracker import HandTracker
from rendering.renderer import Renderer
from interaction.interaction_manager import InteractionManager

# ============================================================
# CONFIGURAÇÕES
# ============================================================

from config import (
    WIDTH,
    HEIGHT,
    MODEL_PATH,
    OBJECT_SIZE,
    SMOOTHING,
    CAMERA_INDEX,
    FPS,
    MIN_HAND_DETECTION_CONFIDENCE,
    MIN_HAND_PRESENCE_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
)

# ============================================================
# PYGAME
# ============================================================

pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

renderer = Renderer(
    screen,
    WIDTH,
    HEIGHT
)

pygame.display.set_caption(
    "Gesture Interface - V5"
)

clock = pygame.time.Clock()

# ============================================================
# HAND TRACKER
# ============================================================

hand_tracker = HandTracker(
    model_path=MODEL_PATH,
    num_hands=2,
    min_hand_detection_confidence=(
        MIN_HAND_DETECTION_CONFIDENCE
    ),
    min_hand_presence_confidence=(
        MIN_HAND_PRESENCE_CONFIDENCE
    ),
    min_tracking_confidence=(
        MIN_TRACKING_CONFIDENCE
    )
)

# ============================================================
# GESTURE ENGINE
# ============================================================

gesture_detector = GestureDetector()

# ============================================================
# WEBCAM
# ============================================================

camera = cv2.VideoCapture(
    CAMERA_INDEX
)

if not camera.isOpened():

    raise RuntimeError(
        "Não foi possível abrir a câmera."
    )

camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    WIDTH
)

camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    HEIGHT
)

# ============================================================
# INTERACTION MANAGER
# ============================================================

interaction_manager = InteractionManager(
    object_x=WIDTH // 2,
    object_y=HEIGHT // 2,
    object_size=OBJECT_SIZE,
    width=WIDTH,
    height=HEIGHT,
    smoothing=SMOOTHING
)

# ============================================================
# LOOP PRINCIPAL
# ============================================================

running = True

while running:

    # ========================================================
    # EVENTOS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

    # ========================================================
    # WEBCAM
    # ========================================================

    success, frame = camera.read()

    if not success:
        continue

    # Espelha a câmera
    frame = cv2.flip(
        frame,
        1
    )

    # ========================================================
    # RGB
    # ========================================================

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # ========================================================
    # DETECÇÃO DAS MÃOS
    # ========================================================

    hands = hand_tracker.detect(
        rgb_frame
    )

    # ========================================================
    # ESTADO DAS MÃOS
    # ========================================================

    left_hand = None
    right_hand = None

    left_gesture = "NO HAND"
    right_gesture = "NO HAND"

    left_openness = 0.0

    # ========================================================
    # SEPARA AS MÃOS
    # ========================================================

    for hand in hands:

        if hand.handedness == "right":

            left_hand = hand

        elif hand.handedness == "left":

            right_hand = hand

    # ========================================================
    # GESTO DA MÃO ESQUERDA
    # ========================================================

    if left_hand:

        left_gesture = gesture_detector.detect(
            left_hand.landmarks
        )

        left_openness = (
            gesture_detector.get_hand_openness(
                left_hand.landmarks
            )
    )

    # ========================================================
    # GESTO DA MÃO DIREITA
    # ========================================================

    if right_hand:

        right_gesture = gesture_detector.detect(
            right_hand.landmarks
        )

        claw_openness = (
            gesture_detector.get_hand_openness(
                right_hand.landmarks
            )
        )   

        print(
            f"GESTURE: {right_gesture} | "
            f"OPENNESS: {claw_openness:.3f}"
        )

    # ========================================================
    # INTERAÇÃO COM O OBJETO
    #
    # MÃO DIREITA → GRAB / MOVE
    # MÃO ESQUERDA → SCALE
    # ========================================================

    if right_hand:

        index_finger = right_hand.index_finger

        index_x = int(
            index_finger.x * WIDTH
        )

        index_y = int(
            index_finger.y * HEIGHT
        )

        interaction_manager.update(
            index_x,
            index_y,
            right_gesture
        )

    else:

        interaction_manager.release()


    # ========================================================
    # ESCALA PELA MÃO ESQUERDA
    # ========================================================

    if left_hand:

        interaction_manager.update_scale(
            left_openness
        )

    else:

        interaction_manager.stop_scale()

    # ========================================================
    # DESENHA AS MÃOS
    # ========================================================

    for hand in hands:

        renderer.draw_hand(
            frame,
            hand
        )

    # ========================================================
    # DESENHA CÂMERA
    # ========================================================

    renderer.draw_camera(
        frame
    )

    # ========================================================
    # DESENHA OBJETO
    # ========================================================

    renderer.draw_object(
        interaction_manager.object_x,
        interaction_manager.object_y,
        interaction_manager.object_size,
        interaction_manager.is_grabbing,
        interaction_manager.is_hovering
    )

    # ========================================================
    # FPS
    # ========================================================

    fps = int(
        clock.get_fps()
    )

    # ========================================================
    # HUD
    # ========================================================

    gesture_text = (
        f"LEFT: {left_gesture} | "
        f"RIGHT: {right_gesture}"
    )

    renderer.draw_hud(
        left_gesture,
        right_gesture,
        fps,
        interaction_manager.is_grabbing,
        interaction_manager.is_hovering
    )

    # ========================================================
    # ATUALIZA
    # ========================================================

    pygame.display.flip()

    clock.tick(FPS)

# ============================================================
# ENCERRAMENTO
# ============================================================

camera.release()

hand_tracker.close()

pygame.quit()