# BankSampah Kampus (UTS Pengembangan dan Operasi)

Bank sampah digital untuk mahasiswa Fakultas Bisnis dan Fakultas Informatika.
Arsitektur microservices, dijalankan dengan Docker Compose, CI/CD dengan GitHub Actions.

## Menjalankan di komputer sendiri

Syarat: Docker Desktop sudah terpasang dan berjalan.

    docker compose up --build

Buka http://localhost:8080

Akun petugas: `petugas01` / `petugas123`. Mahasiswa mendaftar sendiri lewat tab "Daftar mahasiswa".

## Arsitektur

Browser -> gateway (Nginx :8080) -> frontend | auth | setoran | reward | laporan -> PostgreSQL

## Pembagian tugas

Setiap anggota memegang satu service, satu topik container, dan satu topik CI/CD.

| Anggota | Service dan folder | Topik container | Topik CI/CD |
|---|---|---|---|
| Maria Hana Gultom | Auth (`auth/`) | Variabel lingkungan dan secret | Pemicu workflow, job test, matrix |
| Arisanti Nurlaili | Setoran (`setoran/`, `_shared/`) | Container database (volume, healthcheck) | Pengujian otomatis, SKIP_DB_INIT |
| Alvin Charles | Reward (`reward/`, `docker-compose.yml`) | Jaringan antar container, struktur Compose | needs, syarat if, Secrets |
| Josua Daichi | Laporan (`laporan/`, `nginx/`) | Gateway Nginx | Job build-push ke registry |
| Muhammad Aswan Taqiy (ketua) | Frontend (`frontend/`, `.github/`) | Container frontend, pemantauan container | Job deploy |

## CI/CD (.github/workflows/ci-cd.yml)

1. test: pytest pada keempat service (matrix)
2. build-push: build enam image dan push ke ghcr.io
3. deploy: SSH ke server lalu `docker compose pull` dan `docker compose up -d`

Secrets GitHub yang dibutuhkan: `SSH_HOST`, `SSH_USER`, `SSH_KEY`.

## Alur aplikasi

Mahasiswa mengajukan setoran, mengantar sampah, petugas menimbang dan memverifikasi,
poin dihitung (berat x tarif), lalu poin dapat ditukar dengan hadiah.
