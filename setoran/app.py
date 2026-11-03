import os
from flask import Flask, jsonify, request, g
from common import *

app = Flask(__name__)
TARIF_AWAL = [("Botol plastik (PET)", 100), ("Kertas/kardus", 60), ("Kaleng/logam", 150),
              ("Kaca", 40), ("Minyak jelantah", 120)]
COLS = ("id,user_nim,user_nama,fakultas,jenis,berat_est,berat_kg,poin,status,"
        "to_char(tanggal,'YYYY-MM-DD HH24:MI') AS tanggal")


def hitung_poin(berat_kg, poin_per_kg):
    return round(berat_kg * poin_per_kg)


def ke_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def init_db():
    wait_db()
    query("""CREATE TABLE IF NOT EXISTS tarif(
        id SERIAL PRIMARY KEY, jenis TEXT UNIQUE NOT NULL, poin_per_kg INTEGER NOT NULL)""")
    query("""CREATE TABLE IF NOT EXISTS setoran(
        id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, user_nim TEXT, user_nama TEXT, fakultas TEXT,
        jenis TEXT NOT NULL, berat_est DOUBLE PRECISION, berat_kg DOUBLE PRECISION DEFAULT 0,
        poin INTEGER DEFAULT 0, status TEXT NOT NULL DEFAULT 'diajukan',
        tanggal TIMESTAMP DEFAULT now(), petugas_id INTEGER, verifikasi_at TIMESTAMP)""")
    for j, p in TARIF_AWAL:
        query("INSERT INTO tarif(jenis,poin_per_kg) VALUES(%s,%s) ON CONFLICT (jenis) DO NOTHING", (j, p))


@app.get("/health")
def health():
    return jsonify(status="ok", service="setoran")


@app.get("/tarif")
@auth()
def tarif():
    return jsonify(query("SELECT id,jenis,poin_per_kg FROM tarif ORDER BY id"))


@app.put("/tarif/<int:tid>")
@auth(["petugas"])
def ubah_tarif(tid):
    d = request.get_json(force=True, silent=True) or {}
    p = int(ke_float(d.get("poin_per_kg")))
    if p <= 0:
        return jsonify(error="Poin per kg harus lebih dari 0"), 400
    query("UPDATE tarif SET poin_per_kg=%s WHERE id=%s", (p, tid))
    return jsonify(ok=True)


@app.post("/ajukan")
@auth(["warga"])
def ajukan():
    d = request.get_json(force=True, silent=True) or {}
    t = query("SELECT * FROM tarif WHERE id=%s", (d.get("tarif_id"),), one=True)
    berat = ke_float(d.get("berat_est"))
    if not t or berat <= 0:
        return jsonify(error="Pilih jenis sampah dan isi perkiraan berat"), 400
    u = g.user
    query("""INSERT INTO setoran(user_id,user_nim,user_nama,fakultas,jenis,berat_est)
        VALUES(%s,%s,%s,%s,%s,%s)""", (u["uid"], u["nim"], u["nama"], u["fakultas"], t["jenis"], berat))
    return jsonify(ok=True), 201


@app.get("/saya")
@auth(["warga"])
def saya():
    return jsonify(query(f"SELECT {COLS} FROM setoran WHERE user_id=%s ORDER BY id DESC", (g.user["uid"],)))


@app.get("/menunggu")
@auth(["petugas"])
def menunggu():
    return jsonify(query(f"SELECT {COLS} FROM setoran WHERE status='diajukan' ORDER BY id"))


@app.post("/verifikasi/<int:sid>")
@auth(["petugas"])
def verifikasi(sid):
    d = request.get_json(force=True, silent=True) or {}
    berat = ke_float(d.get("berat_kg"))
    if berat <= 0:
        return jsonify(error="Berat hasil timbang harus lebih dari 0"), 400
    s = query("""SELECT s.id, t.poin_per_kg FROM setoran s JOIN tarif t ON t.jenis=s.jenis
        WHERE s.id=%s AND s.status='diajukan'""", (sid,), one=True)
    if not s:
        return jsonify(error="Setoran tidak ditemukan atau sudah diverifikasi"), 404
    poin = hitung_poin(berat, s["poin_per_kg"])
    query("""UPDATE setoran SET berat_kg=%s, poin=%s, status='terverifikasi', petugas_id=%s,
        verifikasi_at=now() WHERE id=%s""", (berat, poin, g.user["uid"], sid))
    return jsonify(ok=True, poin=poin)


# ---- endpoint internal: dipanggil service Reward & Laporan ----
@app.get("/internal/earned/<int:uid>")
@internal
def earned(uid):
    r = query("SELECT COALESCE(SUM(poin),0) AS total FROM setoran WHERE user_id=%s AND status='terverifikasi'",
              (uid,), one=True)
    return jsonify(total=int(r["total"]))


@app.get("/internal/verified")
@internal
def verified():
    return jsonify(query("""SELECT user_id,user_nim,user_nama,fakultas,jenis,berat_kg,poin,
        to_char(verifikasi_at,'YYYY-MM') AS bulan FROM setoran WHERE status='terverifikasi'"""))


if not os.environ.get("SKIP_DB_INIT"):
    init_db()
