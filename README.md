# BankSampah Kampus (UTS Pengembangan dan Operasi)

Bank sampah digital untuk mahasiswa Fakultas Bisnis vs Fakultas Informatika.
Arsitektur microservices, dijalankan dengan Docker Compose, CI/CD dengan GitHub Actions.

## Jalankan lokal
    docker compose up --build
Buka http://localhost:8080

Akun petugas: `petugas01` / `petugas123`. Mahasiswa daftar sendiri lewat tab "Daftar mahasiswa".

## Arsitektur
Browser -> gateway (Nginx :8080) -> frontend | auth | setoran | reward | laporan -> PostgreSQL

| Service  | Penanggung jawab       | Folder     |
|----------|------------------------|------------|
| Auth     | Maria Hana Gultom      | auth/      |
| Setoran  | Arisanti Nurlaili      | setoran/   |
| Reward   | Muhammad Aswan Taqiy   | reward/    |
| Laporan  | Josua Daichi           | laporan/   |
| Frontend + Nginx + Compose + deploy | Alvin Charles | frontend/, nginx/, docker-compose.yml |

## CI/CD (.github/workflows/ci-cd.yml)
1. test: pytest per service (matrix)
2. build-push: build image dan push ke ghcr.io
3. deploy: SSH ke server, `docker compose pull && docker compose up -d`

Secrets GitHub: `SSH_HOST`, `SSH_USER`, `SSH_KEY`. Di server harus ada Docker. Jadikan package ghcr.io berstatus public (atau `docker login ghcr.io` di server).

## Alur
Mahasiswa ajukan setoran -> antar sampah -> petugas timbang & verifikasi -> poin = berat x tarif -> tukar hadiah.
