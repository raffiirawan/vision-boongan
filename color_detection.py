import cv2
import json
import numpy as np
import platform

# --- KONFIGURASI MISI ---
# True = Tampilkan jendela video (Berat, pakai saat testing di Laptop)
# False = Headless mode (Ringan, pakai saat Raspi terbang)
SHOW_VIDEO = True 

# Daftar Model yang mau dipakai
MODEL_FILES = {
    "Blue": "models/blue_model.json",
    "Orange": "models/orange_model.json"
}

# --- LOAD SEMUA MODEL ---
loaded_models = {}
print("Loading Models...")
for name, path in MODEL_FILES.items():
    try:
        with open(path, "r") as f:
            data = json.load(f)
            loaded_models[name] = {
                "lower": np.array(data["lower"]),
                "upper": np.array(data["upper"])
            }
        print(f"    {name} Siap!")
    except Exception as e:
        print(f"    {name} Gagal load: {e}")

if not loaded_models:
    print("Tidak ada model yang dimuat. Keluar.")
    exit()

# --- SETUP KAMERA ---
cap = cv2.VideoCapture(0)
# Set resolusi standar biar tidak terlalu berat
cap.set(3, 640) 
cap.set(4, 480)

print("\nProgram Berjalan! Tekan 'q' untuk keluar.")

while True:
    ret, frame = cap.read()
    if not ret: break

    # Pre-processing (Blur dikit biar noise berkurang)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # Kanvas Hitam untuk "Penglihatan Robot" (Mask Gabungan)
    # Ukurannya sama dengan frame, tapi cuma 1 channel (Hitam Putih)
    combined_mask = np.zeros(frame.shape[:2], dtype="uint8")
    
    status_text = ""

    # --- LOOPING CEK SETIAP WARNA ---
    for name, model in loaded_models.items():
        
        # 1. Buat Masking untuk warna spesifik ini
        mask = cv2.inRange(hsv, model["lower"], model["upper"])
        
        # Bersihkan noise (Erode & Dilate)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        # 2. GABUNGKAN MASK (PENTING!)
        # Kita tumpuk mask Biru & Oranye ke dalam satu layar 'combined_mask'
        # Logika OR: Kalau pixel ini putih di mask Biru ATAU putih di mask Oranye, jadikan putih.
        combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # 3. Cari Kontur untuk menggambar kotak di Layar Real
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            # Ambil objek terbesar
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            
            # Filter ukuran minimum biar gak deteksi semut
            if area > 500: 
                x, y, w, h = cv2.boundingRect(c)
                
                # Tentukan warna kotak berdasarkan target
                # Jika Biru -> Kotak Merah, Jika Orange -> Kotak Biru (Biar kontras)
                box_color = (0, 0, 255) if name == "Blue" else (255, 165, 0)
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
                cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
                
                status_text += f"[{name}: DETECTED] "

    if status_text == "":
        status_text = "SEARCHING..."

    # --- OUTPUT HANDLING ---
    if SHOW_VIDEO:
        # Tampilkan Info Status di Layar Real
        cv2.putText(frame, f"Status: {status_text}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # KAMERA 1: REAL VIEW (Untuk Manusia)
        cv2.imshow("Mata Robot (Real)", frame)
        
        # KAMERA 2: ROBOT VIEW (Untuk Debugging Algoritma)
        # Ini menampilkan apa yang "dilihat" mesin (Putih = Target, Hitam = Abaikan)
        cv2.imshow("Penglihatan Robot (Mask)", combined_mask)

        # Tekan 'q' untuk keluar
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    else:
        # Mode Terbang (Headless)
        # Gunakan \r agar teks tidak spam ke bawah
        print(f"Status: {status_text}" + " " * 20, end='\r')

cap.release()
cv2.destroyAllWindows()