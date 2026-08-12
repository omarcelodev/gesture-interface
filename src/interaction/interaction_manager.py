class InteractionManager:

    def __init__(
        self,
        object_x,
        object_y,
        object_size,
        width,
        height,
        smoothing
    ):

        self.object_x = object_x
        self.object_y = object_y

        self.object_size = object_size

        self.initial_object_size = object_size

        # =================================================
        # LIMITES DE ESCALA
        # =================================================

        self.min_object_size = (
            object_size * 0.5
        )

        self.max_object_size = (
            object_size * 3.0
        )

        self.width = width
        self.height = height

        self.smoothing = smoothing

        self.is_grabbing = False
        self.is_hovering = False
        self.is_scaling = False

        self.grab_offset_x = 0
        self.grab_offset_y = 0

    # ====================================================
    # UTILITÁRIOS
    # ====================================================

    def point_inside_object(
        self,
        point_x,
        point_y
    ):

        distance_x = (
            point_x - self.object_x
        )

        distance_y = (
            point_y - self.object_y
        )

        distance_squared = (
            distance_x ** 2 +
            distance_y ** 2
        )

        radius = self.object_size / 2

        return (
            distance_squared <= radius ** 2
        )

    def lerp(
        self,
        current,
        target
    ):

        return current + (
            target - current
        ) * self.smoothing

    def clamp_object_position(
        self,
        x,
        y
    ):

        radius = self.object_size / 2

        min_x = radius
        max_x = self.width - radius

        min_y = radius
        max_y = self.height - radius

        x = max(
            min_x,
            min(x, max_x)
        )

        y = max(
            min_y,
            min(y, max_y)
        )

        return x, y

    # ====================================================
    # INTERAÇÃO NORMAL
    # ====================================================

    def update(
        self,
        index_x,
        index_y,
        gesture
    ):

        if gesture == "NO HAND":

            self.is_grabbing = False
            self.is_hovering = False

            return

        self.is_hovering = (
            self.point_inside_object(
                index_x,
                index_y
            )
        )

        # =================================================
        # PINCH
        # =================================================

        if gesture == "PINCH":

            # ---------------------------------------------
            # COMEÇOU A SEGURAR
            # ---------------------------------------------

            if not self.is_grabbing:

                if self.is_hovering:

                    self.is_grabbing = True

                    self.grab_offset_x = (
                        self.object_x - index_x
                    )

                    self.grab_offset_y = (
                        self.object_y - index_y
                    )

            # ---------------------------------------------
            # CONTINUA SEGURANDO
            # ---------------------------------------------

            if self.is_grabbing:

                target_x = (
                    index_x +
                    self.grab_offset_x
                )

                target_y = (
                    index_y +
                    self.grab_offset_y
                )

                target_x, target_y = (
                    self.clamp_object_position(
                        target_x,
                        target_y
                    )
                )

                self.object_x = self.lerp(
                    self.object_x,
                    target_x
                )

                self.object_y = self.lerp(
                    self.object_y,
                    target_y
                )

        # =================================================
        # RELEASE
        # =================================================

        else:

            self.is_grabbing = False

    # ====================================================
    # ESCALA PELA ABERTURA DA MÃO
    # ====================================================

    def update_scale(
        self,
        openness
    ):

        self.is_scaling = True

        # ---------------------------------------------
        # GARANTE VALOR ENTRE 0 E 1
        # ---------------------------------------------

        openness = max(
            0.0,
            min(
                openness,
                1.0
            )
        )

        # ---------------------------------------------
        # CONVERTE ABERTURA EM TAMANHO
        # ---------------------------------------------

        target_size = (
            self.min_object_size
            +
            (
                self.max_object_size
                -
                self.min_object_size
            )
            * openness
        )

        # ---------------------------------------------
        # SUAVIZAÇÃO
        # ---------------------------------------------

        self.object_size = self.lerp(
            self.object_size,
            target_size
        )

        # ---------------------------------------------
        # GARANTE OS LIMITES
        # ---------------------------------------------

        self.object_size = max(
            self.min_object_size,
            min(
                self.object_size,
                self.max_object_size
            )
        )

    # ====================================================
    # FINALIZA ESCALA
    # ====================================================

    def stop_scale(self):

        self.is_scaling = False

    # ====================================================
    # RELEASE
    # ====================================================

    def release(self):

        self.is_grabbing = False
        self.is_hovering = False

        self.stop_scale()

    # ====================================================
    # ESTADO
    # ====================================================

    @property
    def object_state(self):

        if self.is_scaling:
            return "SCALING"

        if self.is_grabbing:
            return "GRABBED"

        if self.is_hovering:
            return "HOVER"

        return "FREE"