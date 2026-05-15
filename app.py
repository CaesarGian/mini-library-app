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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)