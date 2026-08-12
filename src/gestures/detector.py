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
    # ÂNGULO ENTRE TRÊS PONTOS
    #
    # point_a → point_b → point_c
    #
    # Retorna o ângulo em graus.
    # ========================================================

    def angle(
        self,
        point_a,
        point_b,
        point_c
    ):

        vector_ba = (
            point_a.x - point_b.x,
            point_a.y - point_b.y
        )

        vector_bc = (
            point_c.x - point_b.x,
            point_c.y - point_b.y
        )

        magnitude_ba = math.sqrt(
            vector_ba[0] ** 2 +
            vector_ba[1] ** 2
        )

        magnitude_bc = math.sqrt(
            vector_bc[0] ** 2 +
            vector_bc[1] ** 2
        )

        if (
            magnitude_ba == 0
            or magnitude_bc == 0
        ):

            return 180.0

        dot_product = (
            vector_ba[0] * vector_bc[0] +
            vector_ba[1] * vector_bc[1]
        )

        cosine = (
            dot_product /
            (magnitude_ba * magnitude_bc)
        )

        # Evita pequenos erros numéricos
        # causarem erro no acos().
        cosine = max(
            -1.0,
            min(
                cosine,
                1.0
            )
        )

        return math.degrees(
            math.acos(cosine)
        )

    # ========================================================
    # VERIFICA SE UM DEDO ESTÁ ESTENDIDO
    # ========================================================

    def finger_is_open(
        self,
        landmarks,
        tip,
        pip
    ):

        return landmarks[tip].y < landmarks[pip].y

    # ========================================================
    # ABERTURA DA MÃO
    #
    # Retorna um valor entre 0.0 e 1.0
    #
    # 0.0 = mão fechada
    # 1.0 = mão aberta
    # ========================================================

    def get_hand_openness(self, landmarks):

        wrist = landmarks[0]

        palm_reference = landmarks[9]

        palm_size = self.distance(
            wrist,
            palm_reference
        )

        if palm_size <= 0:

            return 0.0

        finger_tips = [
            landmarks[8],
            landmarks[12],
            landmarks[16],
            landmarks[20]
        ]

        total_openness = 0.0

        for tip in finger_tips:

            finger_distance = self.distance(
                wrist,
                tip
            )

            normalized_distance = (
                finger_distance /
                palm_size
            )

            finger_openness = (
                normalized_distance - 1.0
            )

            finger_openness = max(
                0.0,
                min(
                    finger_openness,
                    1.0
                )
            )

            total_openness += finger_openness

        openness = (
            total_openness /
            len(finger_tips)
        )

        return openness

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
    # DETECTA CLAW
    #
    # Agora usamos os ângulos das articulações.
    #
    # Um dedo estendido:
    #
    #       TIP
    #        |
    #       PIP
    #        |
    #       MCP
    #
    # → ângulo próximo de 180°
    #
    # Um dedo dobrado:
    #
    #       TIP
    #        \
    #        PIP
    #          \
    #          MCP
    #
    # → ângulo menor.
    # ========================================================

    def is_claw(self, landmarks):

        # ----------------------------------------------------
        # ÂNGULOS DOS QUATRO DEDOS
        # ----------------------------------------------------

        index_angle = self.angle(
            landmarks[8],
            landmarks[6],
            landmarks[5]
        )

        middle_angle = self.angle(
            landmarks[12],
            landmarks[10],
            landmarks[9]
        )

        ring_angle = self.angle(
            landmarks[16],
            landmarks[14],
            landmarks[13]
        )

        pinky_angle = self.angle(
            landmarks[20],
            landmarks[18],
            landmarks[17]
        )

        # ----------------------------------------------------
        # Um CLAW possui dedos curvados.
        #
        # Não queremos exigir um único ângulo exato,
        # porque a mão pode estar em diferentes posições.
        # ----------------------------------------------------

        max_open_angle = 150.0

        index_curved = (
            index_angle < max_open_angle
        )

        middle_curved = (
            middle_angle < max_open_angle
        )

        ring_curved = (
            ring_angle < max_open_angle
        )

        pinky_curved = (
            pinky_angle < max_open_angle
        )

        curved_fingers = sum([
            index_curved,
            middle_curved,
            ring_curved,
            pinky_curved
        ])

        # ----------------------------------------------------
        # Precisamos de pelo menos 3 dedos curvados.
        #
        # Isso permite alguma imperfeição no tracking sem
        # destruir o gesto.
        # ----------------------------------------------------

        return curved_fingers >= 3

    # ========================================================
    # DETECTA GESTO
    # ========================================================

    def detect(self, landmarks):

        # ----------------------------------------------------
        # PINCH
        #
        # Tem prioridade sobre todos os outros gestos.
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
        # CLAW
        # ----------------------------------------------------

        if self.is_claw(landmarks):

            return "CLAW"
        
        # ----------------------------------------------------
        # DESCONHECIDO
        # ----------------------------------------------------

        return "UNKNOWN"