import cv2
import numpy as np
import json
import glob
import os

# ===== KONFIGURASI MODEL =====

MODELS_CONFIG = {
    "BLUE": ["models/blue_model.json", (255, 0, 0)],
    "ORANGE": ["models/orange_model.json", (0, 165, 255)]
}

loaded_models = {}
print("Loading Models...")

for label, config in MODELS_CONFIG.items():
    json_path = config[0]
    box_color = config[1]

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            loaded_models[label] = {
                "lower": np.array(data["lower"]),
                "upper": np.array(data["upper"]),
                "box_color": box_color
            }
        print(f" {label} Loaded")
    except FileNotFoundError:
        print(f" {label} Gagal: File {json_path} tidak ditemukan")

if not loaded_models:
    print("Tidak ada model yang berhasil di-load")
    exit()

# ===== BACA DATA TEST =====

# test_folder = "data_test/**/*.webp"
test_folder = "data_test/*.webp"
test_images = glob.glob(test_folder, recursive=True)

if not test_images:
    print("File tidak ditemukan di: {test_folder}")
    exit()
print(f"Ditemukan {len(test_images)} gambar. Siap test!")

print("\n Mulai test color detection. Klik spasi untuk next. 'q' untuk stop.")
for image_path in test_images:
    frame = cv2.imread(image_path)
    if frame is None: continue

    frame = cv2.resize(frame, (800, 600))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    combined_mask_display = np.zeros(frame.shape[:2], dtype="uint8")

    status_text = ""


# ===== LOOPING CEK SETIAP WARNA =====
    for label, model in loaded_models.items():
        mask = cv2.inRange(hsv, model["lower"], model["upper"])
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        combined_mask_display = cv2.bitwise_or(combined_mask_display, mask)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            if area > 500:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), model["box_color"], 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, model["box_color"], 2)

                if label not in status_text:
                    status_text += f"[{label}]"


    # ===== VISUALISASI =====
    colored_mask = cv2.cvtColor(combined_mask_display, cv2.COLOR_GRAY2BGR)
    colored_mask[:, :, 0] = 0 # Blue channel mati
    colored_mask[:, :, 1] = 0 # Green channel mati
    # Red channel hidup (Visualisasi merah)

    result = cv2.addWeighted(frame, 1, colored_mask, 0.5, 0)

    if status_text == "": status_text = "zonk"

    cv2.putText(result, f"Status: {status_text}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(result, f"File: {os.path.basename(image_path)}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.imshow("Multi-Color Test (Space=Next)", result)


    # === CONTROL LOCK ===

    while True:
        key = cv2.waitKey(100) & 0xff
        if key == ord('q'):
            cv2.destroyAllWindows
            exit()
        elif key == 32:
            break

cv2.destroyAllWindows()