import os, datetime
import jwt
from flask import Flask, jsonify, request, g
from werkzeug.security import generate_password_hash, check_password_hash
from common import *

app = Flask(__name__)


def init_db():
    wait_db()
    query("""CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY, nim TEXT UNIQUE NOT NULL, nama TEXT NOT NULL,
        password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'warga',
        fakultas TEXT NOT NULL DEFAULT '-')""")
    query("""INSERT INTO users(nim,nama,password_hash,role,fakultas)
        VALUES('petugas01','Petugas Bank Sampah',%s,'petugas','-')
        ON CONFLICT (nim) DO NOTHING""", (generate_password_hash("petugas123"),))


def buat_token(u):
    payload = {"uid": u["id"], "nim": u["nim"], "nama": u["nama"], "role": u["role"],
               "fakultas": u["fakultas"],
               "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)}
    return jwt.encode(payload, SECRET, algorithm="HS256")


def publik(u):
    return {"id": u["id"], "nim": u["nim"], "nama": u["nama"], "role": u["role"], "fakultas": u["fakultas"]}


@app.get("/health")
def health():
    return jsonify(status="ok", service="auth")


@app.post("/register")
def register():
    d = request.get_json(force=True, silent=True) or {}
    nim, nama, pw, fak = (d.get("nim", "").strip(), d.get("nama", "").strip(),
                          d.get("password", ""), d.get("fakultas", ""))
    if not nim or not nama or len(pw) < 6:
        return jsonify(error="NIM, nama wajib diisi dan password minimal 6 karakter"), 400
    if fak not in FAKULTAS:
        return jsonify(error="Fakultas harus Bisnis atau Informatika"), 400
    if query("SELECT 1 FROM users WHERE nim=%s", (nim,), one=True):
        return jsonify(error="NIM sudah terdaftar"), 409
    u = query("""INSERT INTO users(nim,nama,password_hash,role,fakultas)
        VALUES(%s,%s,%s,'warga',%s) RETURNING *""", (nim, nama, generate_password_hash(pw), fak), one=True)
    return jsonify(token=buat_token(u), user=publik(u)), 201


@app.post("/login")
def login():
    d = request.get_json(force=True, silent=True) or {}
    u = query("SELECT * FROM users WHERE nim=%s", (d.get("nim", "").strip(),), one=True)
    if not u or not check_password_hash(u["password_hash"], d.get("password", "")):
        return jsonify(error="NIM atau password salah"), 401
    return jsonify(token=buat_token(u), user=publik(u))


@app.get("/me")
@auth()
def me():
    return jsonify(user=g.user)


if not os.environ.get("SKIP_DB_INIT"):
    init_db()
