import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Loanfinder x United E-Bike - B2C RTO")

# 1. Halaman Antarmuka Web (UI Frontend Sederhana)
@app.get("/", response_class=HTMLResponse)
async def read_form():
    return """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Loanfinder x United E-Bike - Pengajuan RTO</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 600px; background: white; margin: 0 auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            h2 { color: #0056b3; margin-top: 0; text-align: center; }
            p.subtitle { text-align: center; color: #666; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; font-weight: 600; margin-bottom: 8px; }
            input[type="text"], input[type="number"], select { width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
            input[type="file"] { padding: 5px 0; }
            button { width: 100%; background-color: #28a745; color: white; border: none; padding: 14px; font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; transition: background 0.3s; }
            button:hover { background-color: #218838; }
            #result { margin-top: 30px; padding: 20px; border-radius: 8px; display: none; }
            .approved { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .rejected { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Formulir Instan Rent-to-Own</h2>
            <p class="subtitle">Analisis AI Loanfinder & United E-Bike (< 10 Menit)</p>
            
            <form id="rtoForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="nama_lengkap">Nama Lengkap (Sesuai KTP):</label>
                    <input type="text" id="nama_lengkap" name="nama_lengkap" required placeholder="Contoh: Budi Santoso">
                </div>
                <div class="form-group">
                    <label for="nik">NIK (16 Digit):</label>
                    <input type="text" id="nik" name="nik" maxlength="16" required placeholder="Contoh: 3273012345678901">
                </div>
                <div class="form-group">
                    <label for="ktp_image">Unggah Foto KTP:</label>
                    <input type="file" id="ktp_image" name="ktp_image" accept="image/*" required>
                </div>
                <div class="form-group">
                    <label for="selfie_image">Unggah Foto Selfie (Liveness Check):</label>
                    <input type="file" id="selfie_image" name="selfie_image" accept="image/*" required>
                </div>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 25px 0;">
                <h3 style="color: #555; font-size: 16px;">Data Penilaian Alternatif (Open Finance)</h3>
                <div class="form-group">
                    <label for="riwayat_listrik">Status Pembayaran Listrik/Token PLN:</label>
                    <select id="riwayat_listrik" name="riwayat_listrik">
                        <option value="LANCAR">Tepat Waktu / Lancar</option>
                        <option value="TERLAMBAT">Pernah Terlambat / Tunggakan</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="rata_belanja_ecommerce">Rata-rata Belanja E-Commerce / Bulan (Rp):</label>
                    <input type="number" id="rata_belanja_ecommerce" name="rata_belanja_ecommerce" value="2500000" required>
                </div>
                <div class="form-group">
                    <label for="rata_mutasi_rekening">Rata-rata Saldo Mengendap di Rekening (Rp):</label>
                    <input type="number" id="rata_mutasi_rekening" name="rata_mutasi_rekening" value="4000000" required>
                </div>
                <button type="submit">Kirim Pengajuan & Hitung Skor</button>
            </form>

            <div id="result"></div>
        </div>

        <script>
            document.getElementById('rtoForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const resultDiv = document.getElementById('result');
                
                resultDiv.style.display = 'block';
                resultDiv.className = '';
                resultDiv.innerHTML = '<em>Sedang memproses dokumen dan menganalisis skor kredit...</em>';

                try {
                    const response = await fetch('/api/v1/rto-assessment', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    
                    if (!response.ok) throw new Error(data.detail || 'Terjadi kesalahan sistem.');

                    if (data.status.includes('APPROVED')) {
                        resultDiv.className = 'approved';
                        resultDiv.innerHTML = `
                            <strong>Status: DISETUJUI</strong><br>
                            ${data.message}<br><br>
                            <strong>Skor Kredit AI:</strong> ${data.credit_score} / 1000 (${data.risk_tier})<br>
                            <strong>Limit Angsuran Maksimal:</strong> Rp ${data.max_monthly_limit.toLocaleString('id-ID')}/bulan<br>
                            <strong>Rekomendasi Unit United:</strong> ${data.recommended_ebike.join(', ')}
                        `;
                    } else {
                        resultDiv.className = 'rejected';
                        resultDiv.innerHTML = `
                            <strong>Status: PERLU TINJAUAN LANJUT / DIKERINGKAN</strong><br>
                            ${data.message}<br><br>
                            <strong>Skor Kredit AI:</strong> ${data.credit_score} / 1000 (${data.risk_tier})
                        `;
                    }
                } catch (error) {
                    resultDiv.className = 'rejected';
                    resultDiv.innerHTML = '<strong>Error:</strong> ' + error.message;
                }
            });
        </script>
    </body>
    </html>
    """

# 2. Logic Machine / Backend Scoring Engine
class RTOResponse(BaseModel):
    status: str
    message: str
    credit_score: int
    risk_tier: str
    max_monthly_limit: float
    recommended_ebike: List[str]

def calculate_alternative_score(token_listrik: str, belanja_ecommerce: float, mutasi_rekening: float) -> int:
    score = 400 # Baseline Score
    
    if belanja_ecommerce > 5000000: score += 250
    elif belanja_ecommerce > 2000000: score += 150
    else: score += 50
        
    if mutasi_rekening > 7000000: score += 250
    elif mutasi_rekening > 3000000: score += 150
    else: score += 50

    if token_listrik.upper() == "LANCAR": score += 100
    else: score -= 50
        
    return min(score, 1000)

@app.post("/api/v1/rto-assessment", response_model=RTOResponse)
async def assess_rto_application(
    ktp_image: UploadFile = File(...),
    selfie_image: UploadFile = File(...),
    nama_lengkap: str = Form(...),
    nik: str = Form(...),
    riwayat_listrik: str = Form(...),
    rata_belanja_ecommerce: float = Form(...),
    rata_mutasi_rekening: float = Form(...)
):
    if len(nik) != 16:
        raise HTTPException(status_code=400, detail="NIK harus 16 digit angka.")
    
    final_score = calculate_alternative_score(riwayat_listrik, rata_belanja_ecommerce, rata_mutasi_rekening)
    
    if final_score >= 800:
        tier, limit = "Tier A (Low Risk)", 1500000.0
        bikes = ["United TX3000 (Motor Listrik)", "United T1800"]
        status = "APPROVED_PREMIUM"
        msg = f"Selamat {nama_lengkap}! Pengajuan Anda lolos otomatis dengan limit premium."
    elif final_score >= 650:
        tier, limit = "Tier B (Medium Risk)", 800000.0
        bikes = ["United MX1200", "United Dresden E-Bike"]
        status = "APPROVED_STANDARD"
        msg = f"Selamat {nama_lengkap}! Pengajuan Anda lolos otomatis untuk tipe standar."
    else:
        tier, limit, bikes = "Tier C (High Risk)", 0.0, []
        status = "REJECTED_NEED_GUARANTOR"
        msg = "Skor Anda belum memenuhi syarat otomatis. Silakan ajukan ulang menggunakan penjamin keluarga dekat."

    return RTOResponse(
        status=status, message=msg, credit_score=final_score,
        risk_tier=tier, max_monthly_limit=limit, recommended_ebike=bikes
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
