import math
from datetime import datetime
from typing import Dict, Any, Tuple

class DynamicFlowModeler:
    """
    Sistem Pemodelan Aliran Dinamis (Dynamic Flow Modeling) [100].
    Melacak tingkat konsentrasi kontaminasi spasial secara real-time 
    selama proses pengolahan kontinu komoditas curah di pabrik.
    """
    def __init__(self, silo_capacity_m3: float = 100.0):
        self.V = silo_capacity_m3  # V(t) - Volume silo aktif saat ini (m3) [101]

    def calculate_transient_mass_balance(
        self,
        current_concentration: float,  # C(t) - Konsentrasi kontaminasi saat ini (skala 0.0 s/d 1.0)
        inflow_rate_m3_min: float,     # Qin(t) - Laju aliran masuk (m3/menit) [101]
        outflow_rate_m3_min: float,    # Qout(t) - Laju aliran keluar (m3/menit) [101]
        incoming_truck_unverified_concentration: float,  # Cin(t) - Konsentrasi truk masuk (1.0 = ilegal) [101]
        time_step_min: float = 1.0     # dt - Jendela integrasi waktu numerik (menit)
    ) -> Tuple[float, float]:
        """
        Kalkulasi integrasi numerik Euler untuk Persamaan Neraca Massa Transien [101]:
        d(V(t) * C(t)) / dt = Qin(t) * Cin(t) - Qout(t) * Cout(t)
        
        Mengembalikan: (Konsentrasi Baru C(t+dt), Volume Baru V(t+dt))
        """
        # 1. dV/dt = Qin - Qout (Laju perubahan volume cairan/butiran di dalam silo)
        dV_dt = inflow_rate_m3_min - outflow_rate_m3_min
        new_V = self.V + dV_dt * time_step_min
        
        # Batasi volume tangki agar tidak melebihi kapasitas fisik (misal max 500 m3)
        new_V = max(min(new_V, 500.0), 1.0)
        
        # 2. d(V*C)/dt = Qin * Cin - Qout * C
        # Persamaan neraca massa transien untuk reaktor pencampuran tangki (CSTR) [101]
        dVC_dt = (inflow_rate_m3_min * incoming_truck_unverified_concentration) - (outflow_rate_m3_min * current_concentration)
        
        # 3. Integrasi Euler untuk pembentukan nilai baru
        new_VC = (self.V * current_concentration) + dVC_dt * time_step_min
        
        # C baru = (V*C) baru / V baru
        new_concentration = new_VC / new_V
        new_concentration = max(min(new_concentration, 1.0), 0.0)
        
        # Perbarui state volume internal
        self.V = new_V
        
        return round(new_concentration, 6), round(new_V, 2)

    def calculate_residence_time_distribution(
        self,
        time_minutes: float,
        mean_residence_time_tau: float
    ) -> float:
        """
        Melacak fungsi distribusi waktu tinggal E(t) [101].
        Membantu memprediksi kapan partikel kargo ilegal mulai keluar dari tangki ke jalur ekspor [101].
        
        Formula PDF CSTR Sempurna:
        E(t) = (1 / tau) * e^(-t / tau)
        """
        if mean_residence_time_tau <= 0:
            return 0.0
        return (1.0 / mean_residence_time_tau) * math.exp(-time_minutes / mean_residence_time_tau)

    def generate_risk_assessment_payload(
        self,
        concentration: float,
        zero_tolerance_threshold: float = 0.001
    ) -> Dict[str, Any]:
        """
        Evaluasi kepatuhan silsilah logistik kontinu secara probabilistik [99].
        Menghasilkan flag sinyal biner yang siap di-read oleh PLC siber-fisik [101].
        """
        # Aturan Kepatuhan Tanpa Toleransi (Zero-Tolerance Threshold) [99]
        is_contaminated = concentration > zero_tolerance_threshold
        
        if is_contaminated:
            status = "HIGH_CONTAMINATION_RISK"
            action_flag = 1  # Sinyal bit 1: Instruksikan katup PLC memotong aliran ke tangki isolasi [102]
            message = f"🚨 ALERT! Tangki terkontaminasi kargo non-compliant. Konsentrasi ({concentration:.4f}) melampaui batas aman ({zero_tolerance_threshold})."
        else:
            status = "SAFE_COMPLIANT_FLOW"
            action_flag = 0  # Sinyal bit 0: Pertahankan katup ke jalur pemrosesan utama [102]
            message = f"✅ Aliran CPO bersih. Konsentrasi ({concentration:.4f}) berada di bawah batas risiko."

        return {
            "assessment_timestamp": datetime.now().isoformat(),
            "silo_current_concentration": concentration,
            "eudr_flow_status": status,
            "plc_hardware_write_register_bit": action_flag, # Flag register PLC
            "message": message
        }