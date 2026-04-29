# simulator.py
# Simulateur Réseau Télécom 4G/5G
# Expose des métriques Prometheus + envoi de logs vers Logstash

import random
import time
import json
import socket
from prometheus_client import start_http_server, Gauge, Counter

# ===============================
# Configuration
# ===============================
UPDATE_INTERVAL = 5   # secondes
LOGSTASH_HOST = "localhost"
LOGSTASH_PORT = 5000

regions = ["Nord", "Centre", "Sud"]
technologies = ["3G", "4G", "5G"]

cellules = [
    {"cellule": "CELL_001", "region": "Nord", "technologie": "4G"},
    {"cellule": "CELL_002", "region": "Nord", "technologie": "5G"},
    {"cellule": "CELL_003", "region": "Centre", "technologie": "4G"},
    {"cellule": "CELL_004", "region": "Sud", "technologie": "5G"},
    {"cellule": "CELL_005", "region": "Sud", "technologie": "3G"},
]

# ===============================
# Métriques Prometheus
# ===============================
telecom_debit_dl_mbps = Gauge(
    "telecom_debit_dl_mbps",
    "Debit download Mbps",
    ["cellule", "region", "technologie"]
)

telecom_debit_ul_mbps = Gauge(
    "telecom_debit_ul_mbps",
    "Debit upload Mbps",
    ["cellule", "region", "technologie"]
)

telecom_latence_ms = Gauge(
    "telecom_latence_ms",
    "Latence reseau ms",
    ["cellule", "region", "technologie"]
)

telecom_rssi_dbm = Gauge(
    "telecom_rssi_dbm",
    "Signal RSSI",
    ["cellule", "region", "technologie"]
)

telecom_sinr_db = Gauge(
    "telecom_sinr_db",
    "SINR",
    ["cellule", "region", "technologie"]
)

telecom_disponibilite_pct = Gauge(
    "telecom_disponibilite_pct",
    "Disponibilite reseau %",
    ["cellule", "region", "technologie"]
)

telecom_utilisateurs_actifs = Gauge(
    "telecom_utilisateurs_actifs",
    "Nombre utilisateurs actifs",
    ["cellule", "region", "technologie"]
)

telecom_perte_paquets_pct = Gauge(
    "telecom_perte_paquets_pct",
    "Perte paquets %",
    ["cellule", "region", "technologie"]
)

telecom_anomalies_total = Counter(
    "telecom_anomalies_total",
    "Total anomalies",
    ["type_anomalie", "cellule"]
)

# ===============================
# Envoi logs vers Logstash
# ===============================
def envoyer_log(level, cellule, message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = {
            "level": level,
            "cellule": cellule,
            "message": message
        }
        sock.sendto(json.dumps(data).encode(), (LOGSTASH_HOST, LOGSTASH_PORT))
        sock.close()
    except:
        pass

# ===============================
# Génération anomalies
# ===============================
def check_anomaly(cellule_id):
    if random.random() < 0.03:
        telecom_anomalies_total.labels(
            type_anomalie="latence",
            cellule=cellule_id
        ).inc()

        envoyer_log(
            "ERROR",
            cellule_id,
            "High latency detected"
        )
        return True
    return False

# ===============================
# Boucle principale
# ===============================
def simulate():
    while True:
        for c in cellules:

            labels = {
                "cellule": c["cellule"],
                "region": c["region"],
                "technologie": c["technologie"]
            }

            anomalie = check_anomaly(c["cellule"])

            # Valeurs normales
            dl = random.uniform(20, 150)
            ul = random.uniform(10, 80)
            lat = random.uniform(15, 80)
            rssi = random.uniform(-95, -60)
            sinr = random.uniform(5, 30)
            dispo = random.uniform(97, 100)
            users = random.randint(10, 300)
            perte = random.uniform(0, 2)

            # Si anomalie
            if anomalie:
                lat = random.uniform(250, 500)
                dl = random.uniform(1, 10)
                perte = random.uniform(5, 15)
                dispo = random.uniform(80, 95)

            telecom_debit_dl_mbps.labels(**labels).set(dl)
            telecom_debit_ul_mbps.labels(**labels).set(ul)
            telecom_latence_ms.labels(**labels).set(lat)
            telecom_rssi_dbm.labels(**labels).set(rssi)
            telecom_sinr_db.labels(**labels).set(sinr)
            telecom_disponibilite_pct.labels(**labels).set(dispo)
            telecom_utilisateurs_actifs.labels(**labels).set(users)
            telecom_perte_paquets_pct.labels(**labels).set(perte)

        print("Métriques mises à jour...")
        time.sleep(UPDATE_INTERVAL)

# ===============================
# Main
# ===============================
if __name__ == "__main__":
    print("Serveur Prometheus lancé sur port 8000")
    start_http_server(8000)
    simulate()