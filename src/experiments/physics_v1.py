import cv2
import pygame
import mediapipe as mp
import math

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gestures.detector import GestureDetector


# ============================================================
# CONFIGURAÇÕES
# ============================================================

WIDTH = 1280
HEIGHT = 720

MODEL_PATH = "models/hand_landmarker.task"

OBJECT_SIZE = 80

# Suavização do movimento da mão
SMOOTHING = 0.25

# Física
GRAVITY = 900.0

# Elasticidade da colisão
BOUNCE = 0.75

# Atrito horizontal
FRICTION = 0.995

# Velocidade máxima do objeto
MAX_VELOCITY = 2500.0


# ============================================================
# PYGAME
# ============================================================

pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Gesture Interface - V5 Physics"
)

clock = pygame.time.Clock()


# ============================================================
# FONTES
# ============================================================

font = pygame.font.Font(
    None,
    32
)


# ============================================================
# MEDIAPIPE
# ============================================================

base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,

    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7,
)

landmarker = vision.HandLandmarker.create_from_options(
    options
)


# ============================================================
# GESTURE ENGINE
# ============================================================

gesture_detector = GestureDetector()


# ============================================================
# WEBCAM
# ============================================================

camera = cv2.VideoCapture(0)

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
# OBJETO
# ============================================================

object_x = WIDTH / 2
object_y = HEIGHT / 2

velocity_x = 0.0
velocity_y = 0.0


# ============================================================
# ESTADOS
# ============================================================

is_grabbing = False
is_hovering = False


# ============================================================
# OFFSET
# ============================================================

grab_offset_x = 0.0
grab_offset_y = 0.0


# ============================================================
# VELOCIDADE DA MÃO
# ============================================================

previous_hand_x = None
previous_hand_y = None

hand_velocity_x = 0.0
hand_velocity_y = 0.0


# ============================================================
# TEMPO
# ============================================================

previous_time = pygame.time.get_ticks()


# ============================================================
# CONEXÕES DA MÃO
# ============================================================

HAND_CONNECTIONS = [

    # Polegar
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),

    # Indicador
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),

    # Médio
    (0, 9),
    (9, 10),
    (10, 11),
    (11, 12),

    # Anelar
    (0, 13),
    (13, 14),
    (14, 15),
    (15, 16),

    # Mindinho
    (0, 17),
    (17, 18),
    (18, 19),
    (19, 20),

    # Palma
    (5, 9),
    (9, 13),
    (13, 17),
]


# ============================================================
# FUNÇÃO: PONTO DENTRO DO OBJETO
# ============================================================

def point_inside_object(
    point_x,
    point_y,
    object_x,
    object_y,
    object_size
):

    distance_x = point_x - object_x
    distance_y = point_y - object_y

    distance_squared = (
        distance_x ** 2 +
        distance_y ** 2
    )

    radius = object_size / 2

    return distance_squared <= radius ** 2


# ============================================================
# FUNÇÃO: LERP
# ============================================================

def lerp(
    current,
    target,
    amount
):

    return current + (
        target - current
    ) * amount


# ============================================================
# FUNÇÃO: LIMITAR VELOCIDADE
# ============================================================

def limit_velocity(
    velocity_x,
    velocity_y
):

    magnitude = math.sqrt(
        velocity_x ** 2 +
        velocity_y ** 2
    )

    if magnitude <= MAX_VELOCITY:

        return velocity_x, velocity_y

    scale = (
        MAX_VELOCITY /
        magnitude
    )

    return (
        velocity_x * scale,
        velocity_y * scale
    )


# ============================================================
# FUNÇÃO: LIMITAR POSIÇÃO
# ============================================================

def clamp_object_position(
    x,
    y
):

    radius = OBJECT_SIZE / 2

    min_x = radius
    max_x = WIDTH - radius

    min_y = radius
    max_y = HEIGHT - radius

    x = max(
        min_x,
        min(x, max_x)
    )

    y = max(
        min_y,
        min(y, max_y)
    )

    return x, y


# ============================================================
# LOOP PRINCIPAL
# ============================================================

running = True


while running:

    # ========================================================
    # DELTA TIME
    # ========================================================

    current_time = pygame.time.get_ticks()

    delta_time = (
        current_time -
        previous_time
    ) / 1000.0

    previous_time = current_time

    # Evita valores absurdos
    delta_time = min(
        delta_time,
        0.033
    )


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
    # MEDIAPIPE
    # ========================================================

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )


    detection_result = landmarker.detect(
        mp_image
    )


    # ========================================================
    # ESTADO PADRÃO
    # ========================================================

    gesture = "NO HAND"

    is_hovering = False


    # ========================================================
    # PROCESSAMENTO DA MÃO
    # ========================================================

    if detection_result.hand_landmarks:

        hand = detection_result.hand_landmarks[0]


        # ----------------------------------------------------
        # GESTO
        # ----------------------------------------------------

        gesture = gesture_detector.detect(
            hand
        )


        # ----------------------------------------------------
        # INDICADOR
        # ----------------------------------------------------

        index_finger = hand[8]

        index_x = (
            index_finger.x *
            WIDTH
        )

        index_y = (
            index_finger.y *
            HEIGHT
        )


        index_x = float(index_x)
        index_y = float(index_y)


        # ====================================================
        # VELOCIDADE DA MÃO
        # ====================================================

        if previous_hand_x is not None:

            hand_velocity_x = (
                index_x -
                previous_hand_x
            ) / delta_time

            hand_velocity_y = (
                index_y -
                previous_hand_y
            ) / delta_time


        previous_hand_x = index_x
        previous_hand_y = index_y


        # ====================================================
        # HOVER
        # ====================================================

        is_hovering = point_inside_object(
            index_x,
            index_y,
            object_x,
            object_y,
            OBJECT_SIZE
        )


        # ====================================================
        # PINCH
        # ====================================================

        if gesture == "PINCH":

            # ------------------------------------------------
            # COMEÇOU A SEGURAR
            # ------------------------------------------------

            if not is_grabbing:

                if is_hovering:

                    is_grabbing = True


                    # Zera velocidade física
                    velocity_x = 0
                    velocity_y = 0


                    # Offset
                    grab_offset_x = (
                        object_x -
                        index_x
                    )

                    grab_offset_y = (
                        object_y -
                        index_y
                    )


            # ------------------------------------------------
            # CONTINUA SEGURANDO
            # ------------------------------------------------

            if is_grabbing:

                target_x = (
                    index_x +
                    grab_offset_x
                )

                target_y = (
                    index_y +
                    grab_offset_y
                )


                # --------------------------------------------
                # SUAVIZAÇÃO
                # --------------------------------------------

                object_x = lerp(
                    object_x,
                    target_x,
                    SMOOTHING
                )

                object_y = lerp(
                    object_y,
                    target_y,
                    SMOOTHING
                )


                # --------------------------------------------
                # ENQUANTO SEGURA
                # OBJETO ACOMPANHA A MÃO
                # --------------------------------------------

                velocity_x = (
                    hand_velocity_x
                )

                velocity_y = (
                    hand_velocity_y
                )


        # ====================================================
        # SOLTOU
        # ====================================================

        else:

            if is_grabbing:

                # --------------------------------------------
                # ARREMESSO
                # --------------------------------------------

                velocity_x = (
                    hand_velocity_x *
                    0.8
                )

                velocity_y = (
                    hand_velocity_y *
                    0.8
                )


            is_grabbing = False


        # ====================================================
        # LANDMARKS
        # ====================================================

        points = []


        for landmark in hand:

            x = int(
                landmark.x *
                WIDTH
            )

            y = int(
                landmark.y *
                HEIGHT
            )

            points.append(
                (x, y)
            )


        # ====================================================
        # CONEXÕES
        # ====================================================

        for start, end in HAND_CONNECTIONS:

            cv2.line(
                frame,
                points[start],
                points[end],
                (0, 255, 255),
                2
            )


        # ====================================================
        # LANDMARKS
        # ====================================================

        for index, point in enumerate(points):

            radius = 6

            if index == 8:

                radius = 10


            cv2.circle(
                frame,
                point,
                radius,
                (0, 255, 255),
                -1
            )


        # ====================================================
        # INDICADOR
        # ====================================================

        cv2.circle(
            frame,
            points[8],
            16,
            (255, 255, 255),
            2
        )


    # ========================================================
    # FÍSICA
    # ========================================================

    if not is_grabbing:

        # ----------------------------------------------------
        # GRAVIDADE
        # ----------------------------------------------------

        velocity_y += (
            GRAVITY *
            delta_time
        )


        # ----------------------------------------------------
        # ATRITO
        # ----------------------------------------------------

        velocity_x *= (
            FRICTION
        )


        # ----------------------------------------------------
        # POSIÇÃO
        # ----------------------------------------------------

        object_x += (
            velocity_x *
            delta_time
        )

        object_y += (
            velocity_y *
            delta_time
        )


        # ----------------------------------------------------
        # LIMITA VELOCIDADE
        # ----------------------------------------------------

        velocity_x, velocity_y = (
            limit_velocity(
                velocity_x,
                velocity_y
            )
        )


        # ====================================================
        # COLISÃO COM ESQUERDA
        # ====================================================

        radius = OBJECT_SIZE / 2


        if object_x - radius <= 0:

            object_x = radius

            velocity_x *= -BOUNCE


        # ====================================================
        # COLISÃO COM DIREITA
        # ====================================================

        if object_x + radius >= WIDTH:

            object_x = WIDTH - radius

            velocity_x *= -BOUNCE


        # ====================================================
        # COLISÃO COM TOPO
        # ====================================================

        if object_y - radius <= 0:

            object_y = radius

            velocity_y *= -BOUNCE


        # ====================================================
        # COLISÃO COM CHÃO
        # ====================================================

        if object_y + radius >= HEIGHT:

            object_y = HEIGHT - radius

            velocity_y *= -BOUNCE


            # Pequeno amortecimento no chão
            velocity_x *= 0.98


            # Evita micro-rebotes infinitos
            if abs(velocity_y) < 80:

                velocity_y = 0


    # ========================================================
    # CONVERTE FRAME
    # ========================================================

    frame_rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    frame_rgb = cv2.transpose(
        frame_rgb
    )


    frame_surface = pygame.surfarray.make_surface(
        frame_rgb
    )


    frame_surface = pygame.transform.scale(
        frame_surface,
        (WIDTH, HEIGHT)
    )


    # ========================================================
    # DESENHA WEBCAM
    # ========================================================

    screen.blit(
        frame_surface,
        (0, 0)
    )


    # ========================================================
    # OBJETO
    # ========================================================

    object_position = (
        int(object_x),
        int(object_y)
    )


    # --------------------------------------------------------
    # GRABBED
    # --------------------------------------------------------

    if is_grabbing:

        pygame.draw.circle(
            screen,
            (255, 255, 255),
            object_position,
            OBJECT_SIZE // 2 + 10,
            3
        )

        pygame.draw.circle(
            screen,
            (0, 220, 255),
            object_position,
            OBJECT_SIZE // 2
        )

        pygame.draw.circle(
            screen,
            (255, 255, 255),
            object_position,
            8
        )


    # --------------------------------------------------------
    # HOVER
    # --------------------------------------------------------

    elif is_hovering:

        pygame.draw.circle(
            screen,
            (255, 255, 255),
            object_position,
            OBJECT_SIZE // 2 + 8,
            3
        )

        pygame.draw.circle(
            screen,
            (0, 220, 255),
            object_position,
            OBJECT_SIZE // 2
        )


    # --------------------------------------------------------
    # NORMAL
    # --------------------------------------------------------

    else:

        pygame.draw.circle(
            screen,
            (0, 220, 255),
            object_position,
            OBJECT_SIZE // 2
        )


    # ========================================================
    # HUD
    # ========================================================

    gesture_text = font.render(
        f"GESTURE: {gesture}",
        True,
        (255, 255, 255)
    )


    screen.blit(
        gesture_text,
        (20, 20)
    )


    # --------------------------------------------------------
    # FPS
    # --------------------------------------------------------

    fps = int(
        clock.get_fps()
    )


    fps_text = font.render(
        f"FPS: {fps}",
        True,
        (255, 255, 255)
    )


    screen.blit(
        fps_text,
        (20, 55)
    )


    # --------------------------------------------------------
    # ESTADO
    # --------------------------------------------------------

    if is_grabbing:

        object_state = "GRABBED"

    elif is_hovering:

        object_state = "HOVER"

    else:

        object_state = "FREE"


    object_text = font.render(
        f"OBJECT: {object_state}",
        True,
        (255, 255, 255)
    )


    screen.blit(
        object_text,
        (20, 90)
    )


    # --------------------------------------------------------
    # VELOCIDADE
    # --------------------------------------------------------

    speed = math.sqrt(
        velocity_x ** 2 +
        velocity_y ** 2
    )


    speed_text = font.render(
        f"SPEED: {int(speed)}",
        True,
        (255, 255, 255)
    )


    screen.blit(
        speed_text,
        (20, 125)
    )


    # ========================================================
    # ATUALIZA
    # ========================================================

    pygame.display.flip()

    clock.tick(60)


# ============================================================
# ENCERRAMENTO
# ============================================================

camera.release()

landmarker.close()

pygame.quit()