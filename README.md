# TobacoGIS-Madura: Aplikasi WebGIS Integrasi Harga Tembakau

Aplikasi Sistem Informasi Geografis Berbasis Web (WebGIS) untuk memantau, memetakan, dan menganalisis transmisi serta integrasi spasial harga komoditas tembakau di sentra produksi Kecamatan Pakong, Kabupaten Pamekasan (Desa Cen Lecen, Desa Lebbek, dan Desa Bicorong).

## Arsitektur & Fitur Utama

1. **Peta Interaktif Spasial (Leaflet.js + GeoJSON PostGIS/SQLite):**
   - Poligon batas tematik kloroplet berdasarkan nilai Elastisitas Transmisi Harga ($E_t$).
   - Titik persebaran kelembagaan Kelompok Tani (Poktan).
   - Tipologi lahan tembakau (Gunung, Tegal, Sawah).
2. **Mesin Kalkulasi Ekonometrika & Transmisi:**
   - Estimasi OLS elastisitas transmisi vertikal: $\ln(P_f) = \alpha_0 + E_t \ln(P_r)$.
   - Perhitungan *Index of Market Connection* (IMC).
   - Simulator dampak kenaikan harga acuan nasional terhadap harga riil petani lokal.
3. **Sistem Peringatan Dini Asimetri Informasi:**
   - Deteksi otomatis anomali pasar oligopsoni / inefisiensi transmisi untuk melindungi posisi tawar petani.

---

## Cara Menjalankan di Google Antigravity / Modern IDE

### Opsi 1: Menjalankan Full-Stack FastAPI (Rekomendasi)

1. Buka terminal Antigravity / IDE di folder proyek:
   ```bash
   cd tobacogis-madura
   ```

2. Pasang dependensi Python:
   ```bash
   pip install -r requirements.txt
   ```

3. Jalankan server aplikasi:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. Akses melalui browser atau Web Preview di Antigravity:vb 
   ```
   http://localhost:8000
   ```
   *Catatan: Basis data SQLite `database/tobacogis.db` akan diinisialisasi dan diisi otomatis (auto-seeded) saat pertama kali dijalankan.*

---

### Opsi 2: Menjalankan Standalone (Zero-Dependency)

Jika Anda ingin langsung melihat dan menguji visualisasi peta dan dashboard tanpa setup server Python:
- Cukup buka file `standalone_app.html` langsung di browser Anda atau gunakan fitur preview HTML di Antigravity.
