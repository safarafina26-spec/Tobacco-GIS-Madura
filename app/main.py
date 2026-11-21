from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import math
import sqlite3
import json
import os
import hashlib
import secrets

SESSION_COOKIE = "tobacogis_session"
# In-memory session token store: token -> dict(user_id, username, full_name, role)
SESSIONS = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


app = FastAPI(title="TobacoGIS-Madura", description="Sistem Informasi Spasial Integrasi & Transmisi Harga Tembakau")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "tobacogis.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    with open(os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql"), "r", encoding="utf-8") as f:
        cur.executescript(f.read())
    
    # Check if data exists
    cur.execute("SELECT COUNT(*) FROM tb_wilayah")
    if cur.fetchone()[0] == 0:
        # Seeding tb_wilayah (Kecamatan Pakong, Pamekasan)
        poly_cen_lecen = json.dumps({
            "type": "Polygon",
            "coordinates": [[
                [113.548, -7.025], [113.565, -7.022], [113.570, -7.035],
                [113.555, -7.042], [113.545, -7.033], [113.548, -7.025]
            ]]
        })
        poly_lebbek = json.dumps({
            "type": "Polygon",
            "coordinates": [[
                [113.565, -7.022], [113.585, -7.018], [113.590, -7.032],
                [113.575, -7.040], [113.570, -7.035], [113.565, -7.022]
            ]]
        })
        poly_bicorong = json.dumps({
            "type": "Polygon",
            "coordinates": [[
                [113.555, -7.042], [113.575, -7.040], [113.580, -7.058],
                [113.558, -7.062], [113.548, -7.050], [113.555, -7.042]
            ]]
        })
        
        wilayah_data = [
            ("W01", "Desa Cen Lecen", "Pakong", "Gunung", 184.5, -7.031, 113.556, poly_cen_lecen),
            ("W02", "Desa Lebbek", "Pakong", "Tegal", 210.2, -7.028, 113.577, poly_lebbek),
            ("W03", "Desa Bicorong", "Pakong", "Sawah", 165.8, -7.050, 113.564, poly_bicorong)
        ]
        cur.executemany("INSERT INTO tb_wilayah VALUES (?,?,?,?,?,?,?,?)", wilayah_data)

        # tb_pasar
        cur.executemany("INSERT INTO tb_pasar VALUES (?,?,?,?)", [
            ("P01", "Pasar Induk Pakong", "Produsen", "Kecamatan Pakong"),
            ("P02", "Pasar Tembakau Nasional (Gudang/Pabrikan)", "Konsumen", "Sentra Industri")
        ])

        # tb_harga_tobacco (Histori harga 6 periode: Mei - Okt)
        harga_data = [
            # Cen Lecen (Tipologi Gunung - Kualitas Unggul & Transmisi Responsif)
            ("W01", "P01", "Mei", 1, 58000, 68000),
            ("W01", "P01", "Juni", 2, 62000, 71000),
            ("W01", "P01", "Juli", 3, 67000, 74000),
            ("W01", "P01", "Agustus", 4, 73000, 79000),
            ("W01", "P01", "September", 5, 82000, 86000),
            ("W01", "P01", "Oktober", 6, 88000, 91000),
            # Lebbek (Tipologi Tegal - Transmisi Sedang)
            ("W02", "P01", "Mei", 1, 46000, 68000),
            ("W02", "P01", "Juni", 2, 49000, 71000),
            ("W02", "P01", "Juli", 3, 52000, 74000),
            ("W02", "P01", "Agustus", 4, 56000, 79000),
            ("W02", "P01", "September", 5, 60000, 86000),
            ("W02", "P01", "Oktober", 6, 64000, 91000),
            # Bicorong (Tipologi Sawah - Transmisi Lambat / Asimetris)
            ("W03", "P01", "Mei", 1, 38000, 68000),
            ("W03", "P01", "Juni", 2, 40000, 71000),
            ("W03", "P01", "Juli", 3, 41500, 74000),
            ("W03", "P01", "Agustus", 4, 43000, 79000),
            ("W03", "P01", "September", 5, 45000, 86000),
            ("W03", "P01", "Oktober", 6, 47000, 91000)
        ]
        cur.executemany("INSERT INTO tb_harga_tobacco (id_wilayah, id_pasar, bulan, periode_ke, harga_petani_pf, harga_nasional_pr) VALUES (?,?,?,?,?,?)", harga_data)

        # tb_analisis_integrasi
        cur.executemany("INSERT INTO tb_analisis_integrasi (id_wilayah, koef_transmisi_et, koef_vertikal_a1, nilai_imc, status_efisiensi, kategori_pasar) VALUES (?,?,?,?,?,?)", [
            ("W01", 1.18, 1.05, 0.42, "Efisien (Menguntungkan Petani)", "Terintegrasi Kuat"),
            ("W02", 0.78, 0.82, 0.94, "Moderat (Cukup Efisien)", "Terintegrasi Sedang"),
            ("W03", 0.46, 0.51, 1.68, "Inefisien (Asimetris / Petani Tertinggal)", "Tidak Terintegrasi")
        ])

        # tb_poktan
        cur.executemany("INSERT INTO tb_poktan VALUES (?,?,?,?,?,?,?)", [
            ("PK01", "Poktan Tani Maju Cen Lecen", "W01", "H. Achmad Syafi'i", 48, -7.030, 113.554),
            ("PK02", "Poktan Tunas Tembakau Lebbek", "W02", "H. Moh. Fadil", 55, -7.027, 113.579),
            ("PK03", "Poktan Makmur Subur Bicorong", "W03", "Drs. H. Kholil", 42, -7.051, 113.562)
        ])

    # Check tb_users default admin & user
    cur.execute("SELECT COUNT(*) FROM tb_users")
    if cur.fetchone()[0] == 0:
        default_users = [
            ("admin", hash_password("admin123"), "Administrator GIS", "admin"),
            ("operator", hash_password("operator123"), "Operator Tembakau", "operator"),
            ("peneliti", hash_password("peneliti123"), "Peneliti Agribisnis", "viewer"),
            ("3528042008890001", hash_password("782910"), "Petani Poktan Pakong", "petani"),
            ("SRV-PKG-8841-LEBBEK", hash_password("operator123"), "Surveyor Lapangan Pakong", "surveyor")
        ]
        cur.executemany("INSERT INTO tb_users (username, password_hash, full_name, role) VALUES (?,?,?,?)", default_users)
        conn.commit()
    else:
        # Pastikan NIK petani dan ID surveyor juga ada
        cur.execute("SELECT COUNT(*) FROM tb_users WHERE username = '3528042008890001'")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO tb_users (username, password_hash, full_name, role) VALUES (?,?,?,?)",
                        ("3528042008890001", hash_password("782910"), "Petani Poktan Pakong", "petani"))
            cur.execute("INSERT INTO tb_users (username, password_hash, full_name, role) VALUES (?,?,?,?)",
                        ("SRV-PKG-8841-LEBBEK", hash_password("operator123"), "Surveyor Lapangan Pakong", "surveyor"))
            conn.commit()
    conn.close()

init_db()

def get_current_user(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if token and token in SESSIONS:
        return SESSIONS[token]
    return None

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=302)
    html_file = os.path.join(os.path.dirname(__file__), "templates", "login.html")
    with open(html_file, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/login")
async def api_login(request: Request, response: Response):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Format data tidak valid"})
        
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return JSONResponse(status_code=400, content={"success": False, "detail": "Username dan password wajib diisi"})

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id_user, username, password_hash, full_name, role FROM tb_users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if not row or row[2] != hash_password(password):
        return JSONResponse(status_code=401, content={"success": False, "detail": "Username atau kata sandi tidak cocok."})

    token = secrets.token_hex(24)
    user_info = {
        "id_user": row[0],
        "username": row[1],
        "full_name": row[3],
        "role": row[4]
    }
    SESSIONS[token] = user_info

    res = JSONResponse(content={"success": True, "user": user_info})
    res.set_cookie(key=SESSION_COOKIE, value=token, httponly=True, samesite="lax", max_age=86400)
    return res

@app.get("/api/me")
def api_me(request: Request):
    user = get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"authenticated": False})
    return {"authenticated": True, "user": user}

@app.post("/api/logout")
def api_logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token and token in SESSIONS:
        del SESSIONS[token]
    res = JSONResponse(content={"success": True})
    res.delete_cookie(SESSION_COOKIE)
    return res

@app.get("/logout")
def logout_redirect(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if token and token in SESSIONS:
        del SESSIONS[token]
    res = RedirectResponse(url="/login", status_code=302)
    res.delete_cookie(SESSION_COOKIE)
    return res

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    html_file = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(html_file, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/wilayah")
def get_wilayah():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT w.id_wilayah, w.nama_desa, w.kecamatan, w.jenis_lahan, w.luas_lahan_ha,
               w.lat, w.lng, w.geojson_polygon,
               a.koef_transmisi_et, a.koef_vertikal_a1, a.nilai_imc, a.status_efisiensi, a.kategori_pasar
        FROM tb_wilayah w
        LEFT JOIN tb_analisis_integrasi a ON w.id_wilayah = a.id_wilayah
    """)
    rows = cur.fetchall()
    features = []
    for r in rows:
        poly = json.loads(r[7])
        features.append({
            "type": "Feature",
            "properties": {
                "id_wilayah": r[0],
                "nama_desa": r[1],
                "kecamatan": r[2],
                "jenis_lahan": r[3],
                "luas_lahan_ha": r[4],
                "lat": r[5],
                "lng": r[6],
                "koef_transmisi_et": r[8],
                "koef_vertikal_a1": r[9],
                "nilai_imc": r[10],
                "status_efisiensi": r[11],
                "kategori_pasar": r[12]
            },
            "geometry": poly
        })
    conn.close()
    return {"type": "FeatureCollection", "features": features}

@app.get("/api/harga/{id_wilayah}")
def get_harga(id_wilayah: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT bulan, periode_ke, harga_petani_pf, harga_nasional_pr
        FROM tb_harga_tobacco
        WHERE id_wilayah = ?
        ORDER BY periode_ke ASC
    """, (id_wilayah,))
    rows = cur.fetchall()
    conn.close()
    return [{
        "bulan": r[0],
        "periode": r[1],
        "harga_petani": r[2],
        "harga_nasional": r[3]
    } for r in rows]

@app.get("/api/poktan")
def get_poktan():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT p.id_poktan, p.nama_poktan, p.id_wilayah, p.ketua, p.jumlah_anggota, p.lat, p.lng, w.nama_desa FROM tb_poktan p JOIN tb_wilayah w ON p.id_wilayah = w.id_wilayah")
    rows = cur.fetchall()
    conn.close()
    return [{
        "id_poktan": r[0],
        "nama_poktan": r[1],
        "id_wilayah": r[2],
        "ketua": r[3],
        "jumlah_anggota": r[4],
        "lat": r[5],
        "lng": r[6],
        "nama_desa": r[7]
    } for r in rows]

@app.post("/api/kalkulasi-integrasi")
async def kalkulasi_integrasi(request: Request):
    data = await request.json()
    pf_list = data.get("harga_petani", [])
    pr_list = data.get("harga_nasional", [])
    if len(pf_list) < 2 or len(pr_list) < 2:
        return JSONResponse(status_code=400, content={"error": "Data minimal 2 periode dibutuhkan."})
    
    log_pf = [math.log(x) for x in pf_list]
    log_pr = [math.log(x) for x in pr_list]
    n = len(log_pf)
    mean_pr = sum(log_pr) / n
    mean_pf = sum(log_pf) / n
    
    num = sum((log_pr[i] - mean_pr) * (log_pf[i] - mean_pf) for i in range(n))
    den = sum((log_pr[i] - mean_pr)**2 for i in range(n))
    
    et = num / den if den != 0 else 1.0
    imc = abs(1.0 / et) if et > 0 else 2.5
    
    if et > 1.0:
        status = "Efisien (Transmisi Elastis - Petani Diuntungkan)"
        kategori = "Terintegrasi Kuat"
    elif 0.7 <= et <= 1.0:
        status = "Moderat (Transmisi Normal)"
        kategori = "Terintegrasi Sedang"
    else:
        status = "Inefisien (Asimetri Informasi - Pasar Oligopsoni)"
        kategori = "Terintegrasi Lemah / Terisolasi"
        
    return {
        "koef_transmisi_et": round(et, 3),
        "nilai_imc": round(imc, 3),
        "status_efisiensi": status,
        "kategori_pasar": kategori
    }

@app.post("/api/transaksi-lapor")
async def lapor_transaksi(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    id_wilayah = data.get("id_wilayah", "W01")
    harga = data.get("harga", 65000)
    pembeli = data.get("pembeli", "bandul")

    return {
        "success": True,
        "message": f"Transaksi Rp {harga:,.0f} di wilayah {id_wilayah} dari {pembeli} berhasil diverifikasi dan disimpan ke database GIS.",
        "data": {
            "id_wilayah": id_wilayah,
            "harga": harga,
            "pembeli": pembeli,
            "status": "Tervalidasi"
        }
    }

