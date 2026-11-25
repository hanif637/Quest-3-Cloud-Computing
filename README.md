# Smart City Jember — The Container Awakening

Aplikasi web sederhana untuk demonstrasi containerization menggunakan Flask dan Docker.

## Isi proyek

- `app.py` — aplikasi Flask dan data contoh sensor.
- `templates/index.html` — halaman dashboard Status Sensor Cuaca Kota Jember.
- `static/style.css` — tampilan dashboard responsif.
- `Dockerfile` — instruksi untuk membangun image Docker.
- `requirements.txt` — dependensi Python.
- `compose.elastic-shield.yaml` — stack monitoring terpisah dari konfigurasi Docker lama.
- `monitoring/` — konfigurasi Prometheus dan provisioning Grafana.
- `load_test.py` — load test HTTP bertahap (tidak dijalankan otomatis).

## 1. Buka folder proyek

Ekstrak ZIP, lalu buka PowerShell atau terminal pada folder `smart-city-jember` (folder yang berisi `Dockerfile`).

## 2. Build image

```powershell
docker build -t smart-city-jember .
```

## 3. Jalankan container dengan NIM

Ganti `NIM_ANDA` dengan NIM asli. Perintah ini memasukkan NIM sebagai environment variable bernama `NIM` ke dalam container.

```powershell
docker run -d --name smart-city-jember -p 5000:5000 -e NIM="NIM_ANDA" smart-city-jember
```

Contoh format (bukan NIM sungguhan):

```powershell
docker run -d --name smart-city-jember -p 5000:5000 -e NIM="2301234567" smart-city-jember
```

## 4. Buka aplikasi

Buka browser ke:

```text
http://localhost:5000
```

NIM yang dikirim melalui `-e NIM=...` akan tampil pada bagian **Identitas Pengguna** di halaman web.

## 5. Verifikasi environment variable (opsional)

```powershell
docker exec smart-city-jember printenv NIM
```

Untuk melihat log:

```powershell
docker logs smart-city-jember
```

Untuk menghentikan dan menghapus container:

```powershell
docker stop smart-city-jember
docker rm smart-city-jember
```

Jika nama container sudah pernah dipakai, jalankan perintah stop dan rm di atas sebelum menjalankan container baru. Image tidak perlu dibangun ulang selama source code tidak berubah.

## Catatan demonstrasi

Nilai suhu dan kelembapan pada dashboard adalah **data simulasi**, bukan data sensor fisik atau data real-time. Tugas ini mendemonstrasikan aplikasi web yang berhasil dijalankan di dalam Docker.

## Elastic Shield: monitoring lokal

Stack ini berjalan berdampingan dengan container lama dan menggunakan port yang berbeda:

- Aplikasi Flask baru: http://localhost:5002 (container lama pada port 5000 tidak disentuh).
- Grafana: http://localhost:3000.
- Prometheus: http://localhost:9090.
- cAdvisor: http://localhost:8080.

1. Salin contoh konfigurasi environment dan ganti password Grafana dengan nilai unik:

   ```powershell
   if (-not (Test-Path .env)) { Copy-Item .env.example .env }
   notepad .env
   ```

   Jangan commit atau membagikan `.env`. Port dashboard monitoring hanya di-bind ke loopback.

2. Validasi lalu jalankan stack:

   ```powershell
   docker compose -f compose.elastic-shield.yaml config
   docker compose -f compose.elastic-shield.yaml up -d --build
   ```

3. Buka aplikasi dan dashboard. Login Grafana menggunakan `GRAFANA_ADMIN_USER` dan
   `GRAFANA_ADMIN_PASSWORD` dari `.env`. Dashboard dan data source Prometheus
   diprovisikan otomatis.

4. Verifikasi aplikasi dan metrik:

   ```powershell
   Invoke-WebRequest http://localhost:5002/health
   Invoke-WebRequest http://localhost:5002/metrics
   ```

   Di Prometheus, periksa **Status > Targets**. Flask dan cAdvisor harus berstatus
   `UP`. Windows Exporter akan berstatus `UP` setelah dipasang dan dijalankan pada host.

5. Untuk menghentikan stack tanpa menghapus datanya:

   ```powershell
   docker compose -f compose.elastic-shield.yaml down
   ```

   Hindari opsi `-v`: volume Prometheus dan Grafana menyimpan data persisten.

### Windows Exporter pada Windows host

Windows Exporter berjalan sebagai layanan pada host Windows, bukan container Linux.
Pasang [rilis MSI Windows Exporter v0.32.1](https://github.com/prometheus-community/windows_exporter/releases/tag/v0.32.1),
aktifkan collector CPU, CS, dan memory, lalu pastikan layanan mendengarkan pada port
9182. Prometheus mengaksesnya melalui
`host.docker.internal:9182`. Batasi firewall ke jaringan lokal/host Docker; jangan
membuka port 9182 ke internet. Instalasi exporter host dilakukan terpisah dari Compose.

### Load test bertahap

Jalankan hanya setelah memastikan aplikasi target milik sendiri dan kapasitas lokal
memadai. Mulai dari `normal`, tinjau metrik, lalu baru lanjut ke `medium` dan `high`.
Script membuat request selama durasi skenario dan timeout per-request membatasi waktu
tunggu; jangan jalankan skenario tinggi pada server produksi.

```powershell
py -m pip install -r requirements.txt
py .\load_test.py --url http://127.0.0.1:5002/ --scenario normal
py .\load_test.py --url http://127.0.0.1:5002/ --scenario medium
py .\load_test.py --url http://127.0.0.1:5002/ --scenario high
```

Target dibatasi ke `localhost`/loopback dan beban khusus dibatasi maksimum 100 user
serta 60 detik. Skenario dapat diubah menggunakan `--users`, `--duration`, dan `--timeout`.
Lihat [DOKUMENTASI-ARSITEKTUR-ELASTIC-SHIELD.md](./DOKUMENTASI-ARSITEKTUR-ELASTIC-SHIELD.md)
untuk arsitektur, keterbatasan autoscaling, keamanan, dan daftar screenshot.

## Alur video demonstrasi (maksimal 3 menit)

1. Perkenalkan diri: sebutkan nama dan NIM, tampilkan wajah dan pastikan suara terdengar.
2. Tampilkan folder proyek dan `Dockerfile` secara singkat.
3. Di terminal pada folder proyek, jalankan `docker build -t smart-city-jember .`.
4. Jalankan `docker run -d --name smart-city-jember -p 5000:5000 -e NIM="NIM_ANDA" smart-city-jember` dengan NIM asli.
5. Buka `http://localhost:5000`, tunjukkan dashboard dan NIM yang tampil.
6. (Opsional) Tunjukkan `docker ps` untuk membuktikan container berjalan.
