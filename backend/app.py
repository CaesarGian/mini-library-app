# app.py — Backend Mini Digital Library
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ──────────────────────────────────────────
# DATA STORE (Hardcoded JSON/Dict — sesuai ketentuan Tugas 9)
# ──────────────────────────────────────────

books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "year": 2008, "stock": 3, "category": "Programming"},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "David Thomas", "year": 1999, "stock": 2, "category": "Programming"},
    {"id": 3, "title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "year": 2017, "stock": 1, "category": "Database"},
    {"id": 4, "title": "Computer Networking: A Top-Down Approach", "author": "Kurose & Ross", "year": 2020, "stock": 4, "category": "Networking"},
    {"id": 5, "title": "Introduction to Algorithms", "author": "Cormen et al.", "year": 2009, "stock": 2, "category": "Algorithm"},
]

members = [
    {"id": 1, "name": "Caesar Gian Indrarizky", "nim": "103012300218", "prodi": "S1 Informatika", "email": "caesar@student.telkomuniversity.ac.id", "active": True},
    {"id": 2, "name": "Tano Hidayat", "nim": "103012300118", "prodi": "S1 Informatika", "email": "tano@student.telkomuniversity.ac.id", "active": True},
    {"id": 3, "name": "Muhammad Lutfi", "nim": "103012300438", "prodi": "S1 Informatika", "email": "lutfi@student.telkomuniversity.ac.id", "active": True},
    {"id": 4, "name": "Muammar Irza Choirruzzat", "nim": "103012330314", "prodi": "S1 Informatika", "email": "irza@student.telkomuniversity.ac.id", "active": True},
    {"id": 5, "name": "Faiz Arrafi", "nim": "103012300304", "prodi": "S1 Informatika", "email": "faiz@student.telkomuniversity.ac.id", "active": True},

]

borrowings = [
    {"id": 1, "book_id": 1, "member_id": 1, "borrow_date": "2026-04-01", "return_date": None, "status": "borrowed"},
    {"id": 2, "book_id": 3, "member_id": 2, "borrow_date": "2026-04-10", "return_date": "2026-04-20", "status": "returned"},
]

next_ids = {"book": 6, "member": 4, "borrowing": 3}


# ──────────────────────────────────────────
# HELPER
# ──────────────────────────────────────────
def find_by_id(collection, item_id):
    return next((x for x in collection if x["id"] == item_id), None)


# ══════════════════════════════════════════
# BOOKS — CRUD
# ══════════════════════════════════════════

@app.route("/api/books", methods=["GET"])
def get_books():
    keyword = request.args.get("q", "").lower()
    result = [b for b in books if keyword in b["title"].lower() or keyword in b["author"].lower()] if keyword else books
    return jsonify({"status": "success", "data": result, "total": len(result)})

@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = find_by_id(books, book_id)
    if not book:
        return jsonify({"status": "error", "message": "Buku tidak ditemukan"}), 404
    return jsonify({"status": "success", "data": book})

@app.route("/api/books", methods=["POST"])
def create_book():
    data = request.get_json()
    required = ["title", "author", "year", "stock", "category"]
    if not all(k in data for k in required):
        return jsonify({"status": "error", "message": "Field tidak lengkap"}), 400
    new_book = {"id": next_ids["book"], **data}
    books.append(new_book)
    next_ids["book"] += 1
    return jsonify({"status": "success", "message": "Buku berhasil ditambahkan", "data": new_book}), 201

@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = find_by_id(books, book_id)
    if not book:
        return jsonify({"status": "error", "message": "Buku tidak ditemukan"}), 404
    data = request.get_json()
    book.update(data)
    return jsonify({"status": "success", "message": "Buku berhasil diupdate", "data": book})

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = find_by_id(books, book_id)
    if not book:
        return jsonify({"status": "error", "message": "Buku tidak ditemukan"}), 404
    books.remove(book)
    return jsonify({"status": "success", "message": "Buku berhasil dihapus"})


# ══════════════════════════════════════════
# MEMBERS — CRUD
# ══════════════════════════════════════════

@app.route("/api/members", methods=["GET"])
def get_members():
    return jsonify({"status": "success", "data": members, "total": len(members)})

@app.route("/api/members/<int:member_id>", methods=["GET"])
def get_member(member_id):
    member = find_by_id(members, member_id)
    if not member:
        return jsonify({"status": "error", "message": "Anggota tidak ditemukan"}), 404
    return jsonify({"status": "success", "data": member})

@app.route("/api/members", methods=["POST"])
def create_member():
    data = request.get_json()
    required = ["name", "nim", "prodi", "email"]
    if not all(k in data for k in required):
        return jsonify({"status": "error", "message": "Field tidak lengkap"}), 400
    new_member = {"id": next_ids["member"], "active": True, **data}
    members.append(new_member)
    next_ids["member"] += 1
    return jsonify({"status": "success", "message": "Anggota berhasil didaftarkan", "data": new_member}), 201

@app.route("/api/members/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    member = find_by_id(members, member_id)
    if not member:
        return jsonify({"status": "error", "message": "Anggota tidak ditemukan"}), 404
    data = request.get_json()
    member.update(data)
    return jsonify({"status": "success", "message": "Anggota berhasil diupdate", "data": member})

@app.route("/api/members/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    member = find_by_id(members, member_id)
    if not member:
        return jsonify({"status": "error", "message": "Anggota tidak ditemukan"}), 404
    members.remove(member)
    return jsonify({"status": "success", "message": "Anggota berhasil dihapus"})


# ══════════════════════════════════════════
# BORROWINGS — CRUD
# ══════════════════════════════════════════

@app.route("/api/borrowings", methods=["GET"])
def get_borrowings():
    enriched = []
    for b in borrowings:
        book = find_by_id(books, b["book_id"])
        member = find_by_id(members, b["member_id"])
        enriched.append({
            **b,
            "book_title": book["title"] if book else "Unknown",
            "member_name": member["name"] if member else "Unknown"
        })
    return jsonify({"status": "success", "data": enriched, "total": len(enriched)})

@app.route("/api/borrowings/<int:borrowing_id>", methods=["PUT"])
def update_borrowing(borrowing_id):
    borrowing = find_by_id(borrowings, borrowing_id)
    if not borrowing:
        return jsonify({"status": "error", "message": "Data peminjaman tidak ditemukan"}), 404
    data = request.get_json()
    borrowing.update(data)
    return jsonify({"status": "success", "message": "Peminjaman diupdate", "data": borrowing})

@app.route("/api/borrowings/<int:borrowing_id>", methods=["DELETE"])
def delete_borrowing(borrowing_id):
    borrowing = find_by_id(borrowings, borrowing_id)
    if not borrowing:
        return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404
    borrowings.remove(borrowing)
    return jsonify({"status": "success", "message": "Data peminjaman dihapus"})


# ══════════════════════════════════════════
# SMART BORROWING — Fitur 2+ entitas (Buku + Anggota + Peminjaman)
# ══════════════════════════════════════════

@app.route("/api/borrow", methods=["POST"])
def smart_borrow():
    data = request.get_json()
    book_id = data.get("book_id")
    member_id = data.get("member_id")

    # Validasi input
    if not book_id or not member_id:
        return jsonify({"status": "error", "message": "book_id dan member_id wajib diisi"}), 400

    # Cek buku ada & tersedia
    book = find_by_id(books, book_id)
    if not book:
        return jsonify({"status": "error", "message": "Buku tidak ditemukan"}), 404
    if book["stock"] < 1:
        return jsonify({"status": "error", "message": f"Stok buku '{book['title']}' habis"}), 400

    # Cek anggota aktif
    member = find_by_id(members, member_id)
    if not member:
        return jsonify({"status": "error", "message": "Anggota tidak terdaftar"}), 404
    if not member["active"]:
        return jsonify({"status": "error", "message": "Akun anggota tidak aktif"}), 403

    # Cek anggota belum pinjam buku yang sama
    existing = next((b for b in borrowings if b["book_id"] == book_id and b["member_id"] == member_id and b["status"] == "borrowed"), None)
    if existing:
        return jsonify({"status": "error", "message": "Anda sudah meminjam buku ini"}), 400

    # Proses peminjaman
    book["stock"] -= 1
    new_borrowing = {
        "id": next_ids["borrowing"],
        "book_id": book_id,
        "member_id": member_id,
        "borrow_date": datetime.now().strftime("%Y-%m-%d"),
        "return_date": None,
        "status": "borrowed"
    }
    borrowings.append(new_borrowing)
    next_ids["borrowing"] += 1

    return jsonify({
        "status": "success",
        "message": f"Berhasil meminjam '{book['title']}'",
        "data": {
            "borrowing": new_borrowing,
            "book": book,
            "member_name": member["name"]
        }
    }), 201


# ══════════════════════════════════════════
# RETURN BOOK
# ══════════════════════════════════════════

@app.route("/api/return/<int:borrowing_id>", methods=["POST"])
def return_book(borrowing_id):
    borrowing = find_by_id(borrowings, borrowing_id)
    if not borrowing:
        return jsonify({"status": "error", "message": "Data peminjaman tidak ditemukan"}), 404
    if borrowing["status"] == "returned":
        return jsonify({"status": "error", "message": "Buku sudah dikembalikan"}), 400

    book = find_by_id(books, borrowing["book_id"])
    if book:
        book["stock"] += 1

    borrowing["status"] = "returned"
    borrowing["return_date"] = datetime.now().strftime("%Y-%m-%d")

    return jsonify({"status": "success", "message": "Buku berhasil dikembalikan", "data": borrowing})


# ══════════════════════════════════════════
# DASHBOARD STATS
# ══════════════════════════════════════════

@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "status": "success",
        "data": {
            "total_books": len(books),
            "total_members": len(members),
            "total_borrowings": len(borrowings),
            "active_borrowings": len([b for b in borrowings if b["status"] == "borrowed"]),
            "returned": len([b for b in borrowings if b["status"] == "returned"]),
        }
    })

# ══════════════════════════════════════════
# AUTH — Login & Register
# ══════════════════════════════════════════

users = [
    {
        "id": 1, "name": "Admin Library", "nim": "ADMIN001",
        "email": "admin@library.ac.id", "password": "admin123",
        "role": "admin", "prodi": "Admin"
    },
    {
        "id": 2, "name": "Caesar Gian Indrarizky", "nim": "103012300218",
        "email": "caesar@student.telkomuniversity.ac.id", "password": "password123",
        "role": "user", "prodi": "S1 Informatika"
    },
    {
        "id": 3, "name": "Tano Hidayat", "nim": "103012300118",
        "email": "tano@student.telkomuniversity.ac.id", "password": "password123",
        "role": "user", "prodi": "S1 Informatika"
    },
    {
        "id": 4, "name": "Muhammad Lutfi", "nim": "103012300438",
        "email": "lutfi@student.telkomuniversity.ac.id", "password": "password123",
        "role": "user", "prodi": "S1 Informatika"
    },
]
next_ids["user"] = 5


@app.route("/api/login", methods=["POST"])
def login():
    data       = request.get_json()
    identifier = data.get("identifier", "").strip()
    password   = data.get("password", "").strip()

    if not identifier or not password:
        return jsonify({"status": "error", "message": "Email/NIM dan password wajib diisi"}), 400

    user = next(
        (u for u in users
         if (u["email"] == identifier or u["nim"] == identifier)
         and u["password"] == password),
        None
    )
    if not user:
        return jsonify({"status": "error", "message": "Email/NIM atau password salah"}), 401

    return jsonify({
        "status":  "success",
        "message": f"Selamat datang, {user['name']}!",
        "data": {
            "id":   user["id"],
            "name": user["name"],
            "nim":  user["nim"],
            "role": user["role"],
            "email": user["email"]
        }
    })


@app.route("/api/register", methods=["POST"])
def register():
    data     = request.get_json()
    required = ["name", "nim", "email", "prodi", "password"]
    if not all(k in data and data[k].strip() for k in required):
        return jsonify({"status": "error", "message": "Semua field wajib diisi"}), 400

    # Cek duplikasi
    if any(u["email"] == data["email"] or u["nim"] == data["nim"] for u in users):
        return jsonify({"status": "error", "message": "Email atau NIM sudah terdaftar"}), 409

    # Tambah ke users
    new_user = {
        "id":       next_ids["user"],
        "name":     data["name"],
        "nim":      data["nim"],
        "email":    data["email"],
        "password": data["password"],
        "role":     "user",
        "prodi":    data["prodi"]
    }
    users.append(new_user)
    next_ids["user"] += 1

    # Otomatis daftarkan sebagai member perpustakaan
    new_member = {
        "id":    next_ids["member"],
        "name":  data["name"],
        "nim":   data["nim"],
        "prodi": data["prodi"],
        "email": data["email"],
        "active": True
    }
    members.append(new_member)
    next_ids["member"] += 1

    return jsonify({
        "status":  "success",
        "message": "Akun berhasil dibuat! Silakan login.",
        "data":    {"name": new_user["name"], "role": "user"}
    }), 201


@app.route("/api/borrowings/monthly", methods=["GET"])
def get_monthly_stats():
    return jsonify({
        "status": "success",
        "data": {
            "labels":   ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Ags","Sep","Okt","Nov","Des"],
            "borrowed": [8,12,7,15,10,18,0,0,0,0,0,0],
            "returned": [6,10,7,12,9,14,0,0,0,0,0,0]
        }
    })


# Endpoint: ambil pinjaman berdasarkan member (untuk user view)
@app.route("/api/borrowings/member/<int:member_id>", methods=["GET"])
def get_my_borrowings(member_id):
    my_borrows = [b for b in borrowings if b["member_id"] == member_id]
    enriched = []
    for b in my_borrows:
        book = find_by_id(books, b["book_id"])
        enriched.append({
            **b,
            "book_title": book["title"] if book else "Unknown"
        })
    return jsonify({"status": "success", "data": enriched})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
