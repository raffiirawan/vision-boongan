from pymavlink import mavutil
import time
import random

# --- SETUP KONEKSI ---
print("Menghubungkan ke SITL...")
connection = mavutil.mavlink_connection('udp:127.0.0.1:14550')
connection.wait_heartbeat()
print("Ready bolo....")

# --- 2. DEFINISI FUNGSI (ACTION) ---
SERVO_PORT = 9
def set_servo(pwm):
    connection.mav.command_long_send(
        connection.target_system, connection.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO, 0,
        SERVO_PORT, pwm, 0, 0, 0, 0, 0
    )

def lock_mechanism():
    print("Mekanisme locked (PWM 1000)")
    set_servo(1000)

def drop_payload():
    print("Barang di drop (PWM 2000)")
    set_servo(2000)

# --- 3. STATE MANAGEMENT (PENTING!) ---
# Ini variabel "ingatan". Supaya robot tau dia udah nge-drop atau belum.
sudah_drop = False

# Kondisi awal: Kunci dulu
lock_mechanism()
time.sleep(2)

# --- 4. LOOPING UTAMA (THE BRAIN) ---
try:
    while True:
        if sudah_drop:
            print("Misi Selesai. Return to Base...")
            break

        # --- SIMULASI VISION ---
        # Anggap ini data dari YOLO (0 - 100%)
        confidence = random.randint(0, 100)
        print(f"Scanning... Confidence Vision: {confidence}%")

        # --- LOGIKA KEPUTUSAN (IF-ELSE) ---
        # Syarat Drop: Yakin > 90% DAN Belum pernah drop sebelumnya
        if confidence > 90 and not sudah_drop:
            print(">>> TARGET TERDETEKSI VALID! SIKAT <<<")
            drop_payload()
            sudah_drop = True
        else:
            print("Target belum jelas...")
    
except KeyboardInterrupt:
    print("Program Berhenti")
