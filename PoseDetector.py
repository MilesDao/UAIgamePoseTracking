import cv2
import mediapipe as mp
import math


class PoseDetector:
    def __init__(
        self,
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ):

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.results = None
        self.lmList = []

    def findPose(self, img, draw=True):
        """Tìm pose trong ảnh và vẽ khung xương nếu cần"""
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)

        if self.results.pose_landmarks and draw:
            h, w, _ = img.shape
            important_ids = [11, 12, 13, 14]
            for idx, lm in enumerate(self.results.pose_landmarks.landmark):
                if idx in important_ids:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 8, (0, 128, 255), cv2.FILLED)
                    cv2.putText(img, str(idx), (cx - 10, cy - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            # Nối vai–khuỷu tay hai bên
            lms = self.results.pose_landmarks.landmark
            points = {i: (int(lms[i].x * w), int(lms[i].y * h)) for i in important_ids}
            if 11 in points and 13 in points:
                cv2.line(img, points[11], points[13], (0, 128, 255), 2)
            if 12 in points and 14 in points:
                cv2.line(img, points[12], points[14], (0, 128, 255), 2)
        return img

    def findPosition(self, img, draw=False):
        """Trả về danh sách tọa độ (id, x, y) của các landmarks"""
        self.lmList = []
        if not self.results or not self.results.pose_landmarks:
            return self.lmList

        h, w, _ = img.shape
        for idx, lm in enumerate(self.results.pose_landmarks.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            self.lmList.append([idx, cx, cy])
            if draw:
                cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)

        return self.lmList

    def findAngle(self, img, p1, p2, p3, draw=True):
        """
        Tính góc tại p2 tạo bởi 3 điểm p1, p2, p3.
        Trả về giá trị góc (0–180°).
        """
        if not self.lmList or len(self.lmList) <= max(p1, p2, p3):
            return 0

        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        # Tính góc (chuẩn hóa 0–180)
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                             math.atan2(y1 - y2, x1 - x2))
        angle = abs(angle)
        if angle > 180:
            angle = 360 - angle

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.line(img, (x2, y2), (x3, y3), (255, 255, 255), 2)
            for (x, y) in [(x1, y1), (x2, y2), (x3, y3)]:
                cv2.circle(img, (x, y), 8, (0, 255, 0), cv2.FILLED)
                cv2.circle(img, (x, y), 12, (0, 255, 0), 2)

        return angle

    def findBoundingBox(self):
        """Trả về bounding box của toàn thân (min_x, min_y, max_x, max_y)"""
        if not self.lmList:
            return None
        xs = [pt[1] for pt in self.lmList]
        ys = [pt[2] for pt in self.lmList]
        return min(xs), min(ys), max(xs), max(ys)


# if __name__ == "__main__":
#     cap = cv2.VideoCapture(0)
#     detector = PoseDetector()

#     while True:
#         success, img = cap.read()
#         if not success:
#             break
#         img = detector.findPose(img)
#         lmList = detector.findPosition(img, draw=False)
#         if lmList:
#             angle = detector.findAngle(img, 11, 13, 15)  # vai–khuỷu–cổ tay
#             cv2.putText(img, f"Angle: {int(angle)}",
#                         (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,
#                         (0, 255, 255), 2)

#         cv2.imshow("Pose Detection", img)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
