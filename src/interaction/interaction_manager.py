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

        self.width = width
        self.height = height

        self.smoothing = smoothing

        self.is_grabbing = False
        self.is_hovering = False

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
    # PROCESSAMENTO
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

    def release(self):

        self.is_grabbing = False
        self.is_hovering = False
        
    # ====================================================
    # ESTADO
    # ====================================================

    @property
    def object_state(self):

        if self.is_grabbing:
            return "GRABBED"

        if self.is_hovering:
            return "HOVER"

        return "FREE"