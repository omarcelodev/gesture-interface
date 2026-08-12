import math


class GestureDetector:

    def __init__(self):
        pass


    # ========================================================
    # DISTÂNCIA ENTRE DOIS PONTOS
    # ========================================================

    def distance(self, point_a, point_b):

        dx = point_a.x - point_b.x
        dy = point_a.y - point_b.y

        return math.sqrt(
            dx ** 2 +
            dy ** 2
        )


    # ========================================================
    # VERIFICA SE UM DEDO ESTÁ ESTENDIDO
    # ========================================================

    def finger_is_open(self, landmarks, tip, pip):

        return landmarks[tip].y < landmarks[pip].y


    # ========================================================
    # DETECTA PINCH
    # ========================================================

    def is_pinch(self, landmarks):

        thumb_tip = landmarks[4]
        index_tip = landmarks[8]

        distance = self.distance(
            thumb_tip,
            index_tip
        )

        return distance < 0.08


    # ========================================================
    # DETECTA GESTO
    # ========================================================

    def detect(self, landmarks):

        # ----------------------------------------------------
        # PINCH
        # ----------------------------------------------------

        if self.is_pinch(landmarks):

            return "PINCH"


        # ----------------------------------------------------
        # DEDOS
        # ----------------------------------------------------

        index_open = self.finger_is_open(
            landmarks,
            8,
            6
        )

        middle_open = self.finger_is_open(
            landmarks,
            12,
            10
        )

        ring_open = self.finger_is_open(
            landmarks,
            16,
            14
        )

        pinky_open = self.finger_is_open(
            landmarks,
            20,
            18
        )


        # ----------------------------------------------------
        # MÃO ABERTA
        # ----------------------------------------------------

        if (
            index_open
            and middle_open
            and ring_open
            and pinky_open
        ):

            return "OPEN_HAND"


        # ----------------------------------------------------
        # INDICADOR
        # ----------------------------------------------------

        if (
            index_open
            and not middle_open
            and not ring_open
            and not pinky_open
        ):

            return "POINT"


        # ----------------------------------------------------
        # PUNHO
        # ----------------------------------------------------

        if (
            not index_open
            and not middle_open
            and not ring_open
            and not pinky_open
        ):

            return "FIST"


        # ----------------------------------------------------
        # DESCONHECIDO
        # ----------------------------------------------------

        return "UNKNOWN"
