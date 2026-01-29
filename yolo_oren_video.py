from ultralytics import YOLO
import cv2

# Load model berat (Small)
model = YOLO("models/small_960.pt") 

video_path = "TRAINING_OREN.mp4"
cap = cv2.VideoCapture(video_path)

# --- SETUP PENYIMPANAN VIDEO ---
# Kita ambil lebar & tinggi dari video asli
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Siapkan penulis video (VideoWriter)
# Hasil akan disimpan sebagai 'hasil_tes_small_960.mp4'
out = cv2.VideoWriter('hasil_tes_small_960.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

print("Sedang memproses... Harap bersabar (memang lambat).")
print("Nanti tonton file 'hasil_tes_small_960.mp4' setelah selesai.")

frame_count = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success: break
    
    frame_count += 1
    # Print progress biar gak dikira hang
    if frame_count % 50 == 0:
        print(f"Memproses frame ke-{frame_count}...")

    # Deteksi (Pakai imgsz sesuai trainingmu, misal 1280)
    # Jika terlalu berat, coba turunkan imgsz=640 dulu untuk tes cepat
    results = model(frame, conf=0.25, imgsz=960, device='cpu') 

    # Gambar kotak di frame
    annotated_frame = results[0].plot()

    # --- SIMPAN KE FILE (JANGAN TAMPILKAN POP-UP) ---
    out.write(annotated_frame)
    
    # Kita matikan cv2.imshow biar laptop fokus rendering saja
    # cv2.imshow("Test", annotated_frame) 
    # if cv2.waitKey(1) & 0xFF == ord("q"): break

cap.release()
out.release() # Penting: Tutup file video
print("Selesai! Silakan buka file 'hasil_tes_small_960.mp4'")