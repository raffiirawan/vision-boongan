from pymavlink import mavutil
import time

# === SETUP KONEKSI SITL ===
print("Menghubungkan ke SITL...")
connection = mavutil.mavlink_connection('udp:127.0.0.1:14550')

# === TUNGGU HEARTBEAT ===
print("Menunggu heartbeat dari pesawat...")
connection.wait_heartbeat()

print(f"Sukses terhubung ke pesawat {connection.target_system}, Component {connection.target_component}")

# === BACA DATA ATTITUDE ===
msg_attitude = connection.recv_match(type='ATTITUDE', blocking=True)
print(f"Data Telemetri diterima -> Roll: {msg_attitude.roll}, Pitch: {msg_attitude.pitch}, Yaw: {msg_attitude.yaw}")

# === BACA DATA BATTERY STATUS ===
msg_battery = connection.recv_match(type='BATTERY_STATUS', blocking=True)
print(f"Data Telemetri diterima -> Baterai: {msg_battery.battery_remaining}%")

# === LOOP UNTUK MENERIMA PESAN TERUS-MENERUS ===
# while True:
#     msg = connection.recv_match(blocking=True)
#     print(msg.get_type(), msg)