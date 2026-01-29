from ultralytics import YOLO
import cv2

# Load model hasil training dari Colab
model = YOLO("models/small_960.pt") 

# Buka video
cap = cv2.VideoCapture("TRAINING_OREN.mp4")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # --- TRIK AGAR RINGAN DI CPU ---
    # 1. Resize tampilan visualisasi (Bukan resize data masuk ke AI)
    # Ini biar window aplikasinya gak kegedean dan berat render-nya
    display_frame = cv2.resize(frame, (800, 600)) 

    # 2. Deteksi
    # device='cpu' --> Memastikan dia tidak bingung cari GPU NVIDIA
    # imgsz=960 --> Sesuai dengan ukuran training model small_960.pt
    results = model(frame, conf=0.25, imgsz=960, device='cpu') 

    # 3. Gambar Kotak Hasil
    annotated_frame = results[0].plot()

    # Tampilkan
    # Kita resize lagi outputnya biar pas di layar laptop
    final_view = cv2.resize(annotated_frame, (1024, 768))
    cv2.imshow("YOLO CPU Test", final_view)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()