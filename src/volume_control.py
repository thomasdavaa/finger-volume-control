"""
Volume Control via Hand Finger Detection
=========================================
Mengendalikan volume Windows menggunakan jumlah jari yang terangkat,
dideteksi lewat kamera menggunakan MediaPipe Hands.

Logika:
    - Setiap jari yang terangkat = 10% volume
    - 0 jari  -> volume 0%
    - 10 jari (kedua tangan, 5 jari masing-masing) -> volume 100%

Dependensi: OpenCV, MediaPipe, pycaw, comtypes (khusus Windows).
"""

import cv2
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_draw

# Pustaka kontrol audio Windows via COM langsung
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, GUID
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# ========================================================
# KONTROL AUDIO WINDOWS INITIALIZATION (CARA DIRECT COM)
# ========================================================
device_enumerator = AudioUtilities.GetDeviceEnumerator()
speakers = device_enumerator.GetDefaultAudioEndpoint(0, 0)
interface = speakers.Activate(GUID(IAudioEndpointVolume._iid_), CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# ========================================================

# 1. Inisialisasi MediaPipe Hands (Maksimal 2 tangan)
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5,
)

# 2. Buka Kamera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Kustomisasi warna kerangka (Biru untuk titik, Putih untuk garis)
dot_styles = mp_draw.DrawingSpec(color=(255, 0, 0), thickness=5, circle_radius=5)
line_styles = mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2)

# ID landmark ujung jari (index, tengah, manis, kelingking) sesuai MediaPipe Hands
FINGER_TIPS = [8, 12, 16, 20]

print("Aplikasi Volume Jari berjalan... Tekan 'q' untuk keluar.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Balik gambar secara horizontal (efek cermin)
    frame = cv2.flip(frame, 1)

    # Konversi format warna ke RGB untuk MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 3. Proses deteksi tangan
    results = hands.process(rgb_frame)

    total_fingers_raised = 0

    # Jika ada tangan yang terdeteksi
    if results.multi_hand_landmarks:
        for hand_landmarks, hand_info in zip(
            results.multi_hand_landmarks, results.multi_handedness
        ):
            hand_label = hand_info.classification[0].label
            landmarks = hand_landmarks.landmark

            fingers_up = 0

            # A. Logika untuk 4 Jari (index, tengah, manis, kelingking)
            for tip in FINGER_TIPS:
                if landmarks[tip].y < landmarks[tip - 2].y:
                    fingers_up += 1

            # B. Logika khusus untuk Jempol (arah horizontal dibalik sesuai tangan)
            if hand_label == "Right":
                thumb_up = 1 if landmarks[4].x < landmarks[3].x else 0
            else:
                thumb_up = 1 if landmarks[4].x > landmarks[3].x else 0

            total_fingers_raised += fingers_up + thumb_up

            # Gambar kerangka tangan
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=dot_styles,
                connection_drawing_spec=line_styles,
            )

        # ========================================================
        # LOGIKA MENGUBAH VOLUME SISTEM
        # ========================================================
        total_fingers_raised = min(total_fingers_raised, 10)
        target_volume = total_fingers_raised / 10.0

        try:
            # Mengubah volume Windows berdasarkan persentase (0.0 sampai 1.0)
            volume.SetMasterVolumeLevelScalar(target_volume, None)
        except Exception:
            pass
        # ========================================================

    # 4. Tampilkan ke jendela OpenCV (Polos tanpa teks)
    cv2.imshow("Volume Control 10 Jari", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()