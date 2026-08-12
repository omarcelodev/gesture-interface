import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from tracking.hand import Hand


class HandTracker:

    def __init__(
        self,
        model_path,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.7,
        min_tracking_confidence=0.7
    ):

        base_options = python.BaseOptions(
            model_asset_path=model_path
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=num_hands,
            min_hand_detection_confidence=(
                min_hand_detection_confidence
            ),
            min_hand_presence_confidence=(
                min_hand_presence_confidence
            ),
            min_tracking_confidence=(
                min_tracking_confidence
            )
        )

        self.landmarker = (
            vision.HandLandmarker.create_from_options(
                options
            )
        )

    def detect(self, rgb_frame):

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        detection_result = self.landmarker.detect(
            mp_image
        )

        hands = []

        if not detection_result.hand_landmarks:
            return hands

        for index, landmarks in enumerate(
            detection_result.hand_landmarks
        ):

            handedness = None
            confidence = 0.0

            if (
                detection_result.handedness
                and index < len(
                    detection_result.handedness
                )
            ):

                category = (
                    detection_result
                    .handedness[index][0]
                )

                handedness = category.category_name.lower()
                confidence = category.score

            hand = Hand(
                landmarks=landmarks,
                handedness=handedness,
                confidence=confidence
            )

            hands.append(hand)

        return hands

    def close(self):

        self.landmarker.close()