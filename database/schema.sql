-- Schema TobacoGIS-Madura (PostgreSQL/PostGIS or SQLite compatible)
CREATE TABLE IF NOT EXISTS tb_wilayah (
    id_wilayah VARCHAR(10) PRIMARY KEY,
    nama_desa VARCHAR(50) NOT NULL,
    kecamatan VARCHAR(50) NOT NULL,
    jenis_lahan VARCHAR(20) NOT NULL, -- Gunung, Tegal, Sawah
    luas_lahan_ha REAL NOT NULL,
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    geojson_polygon TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_pasar (
    id_pasar VARCHAR(10) PRIMARY KEY,
    nama_pasar VARCHAR(50) NOT NULL,
    tingkat_pasar VARCHAR(20) NOT NULL, -- Produsen, Konsumen
    lokasi VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_harga_tobacco (
    id_harga INTEGER PRIMARY KEY AUTOINCREMENT,
    id_wilayah VARCHAR(10) NOT NULL,
    id_pasar VARCHAR(10) NOT NULL,
    bulan VARCHAR(20) NOT NULL,
    periode_ke INTEGER NOT NULL,
    harga_petani_pf REAL NOT NULL,
    harga_nasional_pr REAL NOT NULL,
    FOREIGN KEY(id_wilayah) REFERENCES tb_wilayah(id_wilayah),
    FOREIGN KEY(id_pasar) REFERENCES tb_pasar(id_pasar)
);

CREATE TABLE IF NOT EXISTS tb_analisis_integrasi (
    id_analisis INTEGER PRIMARY KEY AUTOINCREMENT,
    id_wilayah VARCHAR(10) NOT NULL,
    koef_transmisi_et REAL NOT NULL,
    koef_vertikal_a1 REAL NOT NULL,
    nilai_imc REAL NOT NULL,
    status_efisiensi VARCHAR(50) NOT NULL,
    kategori_pasar VARCHAR(50) NOT NULL,
    FOREIGN KEY(id_wilayah) REFERENCES tb_wilayah(id_wilayah)
);

CREATE TABLE IF NOT EXISTS tb_poktan (
    id_poktan VARCHAR(10) PRIMARY KEY,
    nama_poktan VARCHAR(100) NOT NULL,
    id_wilayah VARCHAR(10) NOT NULL,
    ketua VARCHAR(50) NOT NULL,
    jumlah_anggota INTEGER NOT NULL,
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    FOREIGN KEY(id_wilayah) REFERENCES tb_wilayah(id_wilayah)
);

CREATE TABLE IF NOT EXISTS tb_users (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'operator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

