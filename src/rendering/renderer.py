import cv2
import pygame
import math


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


class Renderer:

    def __init__(
        self,
        screen,
        width,
        height
    ):

        self.screen = screen
        self.width = width
        self.height = height

        self.font = pygame.font.Font(
            None,
            32
        )

    # ========================================================
    # CÂMERA
    # ========================================================

    def draw_camera(self, frame):

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
            (self.width, self.height)
        )

        self.screen.blit(
            frame_surface,
            (0, 0)
        )

    # ========================================================
    # MÃO
    # ========================================================

    def draw_hand(self, frame, hand):

        points = []

        # ----------------------------------------------------
        # LANDMARKS
        # ----------------------------------------------------

        for landmark in hand.landmarks:

            x = int(
                landmark.x * self.width
            )

            y = int(
                landmark.y * self.height
            )

            points.append(
                (x, y)
            )

        # ----------------------------------------------------
        # PROTEÇÃO
        # ----------------------------------------------------

        if len(points) != 21:
            return

        # ----------------------------------------------------
        # COR DA MÃO
        # ----------------------------------------------------

        if hand.is_left:

            line_color = (0, 255, 255)

        else:

            line_color = (255, 0, 255)

        # ====================================================
        # CONEXÕES
        # ====================================================

        for start, end in HAND_CONNECTIONS:

            cv2.line(
                frame,
                points[start],
                points[end],
                line_color,
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
                line_color,
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
    # OBJETO
    # ========================================================

    def draw_object(
        self,
        object_x,
        object_y,
        object_size,
        is_grabbing,
        is_hovering,
        rotation
    ):

        object_position = (
            int(object_x),
            int(object_y)
        )

        # ----------------------------------------------------
        # GRABBED
        # ----------------------------------------------------

        if is_grabbing:

            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                object_position,
                object_size // 2 + 10,
                3
            )

            pygame.draw.circle(
                self.screen,
                (0, 220, 255),
                object_position,
                object_size // 2
            )

            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                object_position,
                8
            )

        # ----------------------------------------------------
        # HOVER
        # ----------------------------------------------------

        elif is_hovering:

            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                object_position,
                object_size // 2 + 8,
                3
            )

            pygame.draw.circle(
                self.screen,
                (0, 220, 255),
                object_position,
                object_size // 2
            )

        # ----------------------------------------------------
        # NORMAL
        # ----------------------------------------------------

        else:

            pygame.draw.circle(
                self.screen,
                (0, 220, 255),
                object_position,
                object_size // 2
            )

        # ====================================================
        # REFERÊNCIA DE ROTAÇÃO
        # ====================================================

        radius = object_size // 2

        angle_rad = math.radians(
            rotation
        )

        line_length = radius * 0.75

        end_x = int(
            object_x +
            math.cos(angle_rad) * line_length
        )

        end_y = int(
            object_y +
            math.sin(angle_rad) * line_length
        )

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            object_position,
            (end_x, end_y),
            4
        )

        pygame.draw.circle(
        self.screen,
        (255, 255, 255),
        (end_x, end_y),
        6
)

    # ========================================================
    # HUD
    # ========================================================

    def draw_hud(
        self,
        left_gesture,
        right_gesture,
        fps,
        is_grabbing,
        is_hovering
    ):

        gesture_text = self.font.render(
            f"LEFT: {left_gesture}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            gesture_text,
            (20, 20)
        )

        right_text = self.font.render(
            f"RIGHT: {right_gesture}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            right_text,
            (20, 55)
        )

        fps_text = self.font.render(
            f"FPS: {fps}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            fps_text,
            (20, 90)
        )

        if is_grabbing:

            object_state = "GRABBED"

        elif is_hovering:

            object_state = "HOVER"

        else:

            object_state = "FREE"

        object_text = self.font.render(
            f"OBJECT: {object_state}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            object_text,
            (20, 125)
        )