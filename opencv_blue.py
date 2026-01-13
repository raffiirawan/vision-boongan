import cv2
import numpy as np

# --- 1. SETUP MANUAL (HARDCODED) ---
# Kita tentukan sendiri "Biru itu apa" berdasarkan teori.
# Hue Biru di OpenCV = sekitar 120.
# Kita ambil range aman +/- 20 (100 s.d 140).
# Saturation & Value kita set agak tinggi biar gak nangkep warna abu-abu.

# Format: [Hue, Saturation, Value]
lower_blue = np.array([100, 150, 50]) 
upper_blue = np.array([140, 255, 255])

print(f"🔵 Mode Manual Aktif.")
print(f"   Range Biru: {lower_blue} s/d {upper_blue}")

# --- 2. SETUP KAMERA ---
cap = cv2.VideoCapture(0)

print("🚀 Tekan 'q' untuk STOP.")

while True:
    ret, frame = cap.read()
    if not ret: break

    # Resize untuk simulasi
    frame = cv2.resize(frame, (640, 480))
    total_pixels = frame.shape[0] * frame.shape[1]

    # Convert ke HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # --- DETEKSI MANUAL ---
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Bersihkan noise
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # --- HITUNG DATA ---
    target_pixels = cv2.countNonZero(mask)
    percentage = (target_pixels / total_pixels) * 100

    status = "SEARCHING..."
    color_text = (0, 0, 255) # Merah

    # Visualisasi Kontur
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        # Ambil kontur terbesar
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 500: # Filter noise kecil
            status = "BLUE DETECTED"
            color_text = (255, 0, 0) # Biru
            
            # Gambar kotak di sekitar benda biru
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Target", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Info Teks
    info = f"Blue Coverage: {percentage:.2f}% | {status}"
    cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_text, 2)

    # Tampilkan
    cv2.imshow("Deteksi Manual (General Blue)", frame)
    cv2.imshow("Mask Manual", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()