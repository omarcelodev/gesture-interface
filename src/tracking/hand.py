from dataclasses import dataclass


@dataclass
class Hand:

    landmarks: list
    handedness: str | None = None
    confidence: float = 0.0

    @property
    def index_finger(self):
        return self.landmarks[8]

    @property
    def wrist(self):
        return self.landmarks[0]

    @property
    def thumb(self):
        return self.landmarks[4]

    @property
    def is_left(self):
        return (
            self.handedness is not None
            and self.handedness.lower() == "left"
        )

    @property
    def is_right(self):
        return (
            self.handedness is not None
            and self.handedness.lower() == "right"
        )
