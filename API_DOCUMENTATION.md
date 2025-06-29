# API Documentation - Tanam Rawat

**Versi:** 1.0 MVP  
**Base URL:** `http://127.0.0.1:8000`  
**Otentikasi:** JWT Bearer Token

## 📋 Daftar Isi

1. [Otentikasi](#otentikasi)
2. [Manajemen Tanaman](#manajemen-tanaman)
3. [Jadwal Perawatan](#jadwal-perawatan)
4. [Hama & Penyakit](#hama--penyakit)
5. [Forum Komunitas](#forum-komunitas)
6. [Identifikasi AI](#identifikasi-ai)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## 🔐 Otentikasi

### Registrasi Pengguna

**Endpoint:** `POST /register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true
}
```

**Error Responses:**
- `400 Bad Request` - Email sudah terdaftar
- `422 Unprocessable Entity` - Format email tidak valid

### Login

**Endpoint:** `POST /token`

**Request Body (Form Data):**
```
username=user@example.com
password=password123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized` - Email atau password salah

### Info Pengguna Saat Ini

**Endpoint:** `GET /users/me/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true
}
```

---

## 🌱 Manajemen Tanaman

### Daftar Semua Tanaman

**Endpoint:** `GET /plants/`

**Query Parameters:**
- `skip` (optional): Offset untuk pagination (default: 0)
- `limit` (optional): Jumlah data per halaman (default: 100)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "nama_ilmiah": "Monstera deliciosa",
    "nama_lokal": "Janda Bolong",
    "deskripsi": "Tanaman hias dengan daun berlubang khas",
    "kebutuhan_air": "2-3 hari sekali",
    "intensitas_cahaya": "Cahaya tidak langsung",
    "jenis_media_tanam": "Tanah humus dengan drainase baik",
    "jadwal_pemupukan": "2 minggu sekali"
  }
]
```

### Detail Tanaman

**Endpoint:** `GET /plants/{plant_id}`

**Path Parameters:**
- `plant_id`: ID tanaman (integer)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "nama_ilmiah": "Monstera deliciosa",
  "nama_lokal": "Janda Bolong",
  "deskripsi": "Tanaman hias dengan daun berlubang khas",
  "kebutuhan_air": "2-3 hari sekali",
  "intensitas_cahaya": "Cahaya tidak langsung",
  "jenis_media_tanam": "Tanah humus dengan drainase baik",
  "jadwal_pemupukan": "2 minggu sekali"
}
```

**Error Responses:**
- `404 Not Found` - Tanaman tidak ditemukan

### Tambah Tanaman Baru

**Endpoint:** `POST /plants/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "nama_ilmiah": "Sansevieria trifasciata",
  "nama_lokal": "Lidah Mertua",
  "deskripsi": "Tanaman hias tahan kering dengan daun tegak",
  "kebutuhan_air": "1 minggu sekali",
  "intensitas_cahaya": "Cahaya rendah hingga sedang",
  "jenis_media_tanam": "Tanah kaktus atau tanah biasa dengan drainase baik",
  "jadwal_pemupukan": "1 bulan sekali"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "nama_ilmiah": "Sansevieria trifasciata",
  "nama_lokal": "Lidah Mertua",
  "deskripsi": "Tanaman hias tahan kering dengan daun tegak",
  "kebutuhan_air": "1 minggu sekali",
  "intensitas_cahaya": "Cahaya rendah hingga sedang",
  "jenis_media_tanam": "Tanah kaktus atau tanah biasa dengan drainase baik",
  "jadwal_pemupukan": "1 bulan sekali"
}
```

### Update Tanaman

**Endpoint:** `PUT /plants/{plant_id}`

**Path Parameters:**
- `plant_id`: ID tanaman (integer)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:** (sama dengan POST)

**Response (200 OK):** (sama dengan GET detail)

### Hapus Tanaman

**Endpoint:** `DELETE /plants/{plant_id}`

**Path Parameters:**
- `plant_id`: ID tanaman (integer)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Plant deleted successfully"
}
```

---

## 📅 Jadwal Perawatan

### Daftar Jadwal

**Endpoint:** `GET /schedules/`

**Query Parameters:**
- `skip` (optional): Offset untuk pagination
- `limit` (optional): Jumlah data per halaman

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "plant_id": 1,
    "user_id": 1,
    "task_type": "watering",
    "frequency_days": 3,
    "next_due_date": "2025-07-02T10:00:00",
    "is_active": true,
    "notes": "Siram pagi hari"
  }
]
```

### Buat Jadwal Baru

**Endpoint:** `POST /schedules/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "plant_id": 1,
  "task_type": "watering",
  "frequency_days": 3,
  "next_due_date": "2025-07-02T10:00:00",
  "notes": "Siram pagi hari"
}
```

---

## 🐛 Hama & Penyakit

### Daftar Hama & Penyakit

**Endpoint:** `GET /pest_diseases/`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Kutu Daun",
    "type": "pest",
    "description": "Serangga kecil yang menghisap cairan tanaman",
    "symptoms": "Daun menguning, lengket, pertumbuhan terhambat",
    "treatment": "Semprot dengan insektisida atau larutan sabun",
    "prevention": "Jaga kebersihan area tanaman, hindari kelembaban berlebih"
  }
]
```

---

## 💬 Forum Komunitas

### Daftar Postingan

**Endpoint:** `GET /posts/`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Tips Merawat Monstera",
    "content": "Sharing pengalaman merawat monstera selama 2 tahun...",
    "owner_id": 1,
    "created_at": "2025-06-29T10:00:00",
    "updated_at": "2025-06-29T10:00:00"
  }
]
```

### Buat Postingan Baru

**Endpoint:** `POST /posts/`

**Request Body:**
```json
{
  "title": "Masalah Daun Menguning",
  "content": "Tanaman saya daunnya mulai menguning, ada yang tahu penyebabnya?"
}
```

### Daftar Komentar

**Endpoint:** `GET /comments/`

**Query Parameters:**
- `post_id` (optional): Filter komentar berdasarkan ID postingan

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "content": "Coba kurangi frekuensi penyiraman",
    "post_id": 1,
    "owner_id": 2,
    "created_at": "2025-06-29T11:00:00"
  }
]
```

---

## 🤖 Identifikasi AI

### Identifikasi Tanaman

**Endpoint:** `POST /identify`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
file: <image_file>
```

**Supported Image Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)

**Max File Size:** 10MB

**Response (200 OK):**
```json
{
  "plant_name": "Monstera Deliciosa",
  "confidence": 0.87,
  "description": "Tanaman ini teridentifikasi sebagai Monstera Deliciosa dengan tingkat kepercayaan 87%",
  "care_tips": [
    "Letakkan di tempat dengan cahaya tidak langsung",
    "Siram ketika tanah terasa kering",
    "Berikan pupuk setiap 2-4 minggu sekali"
  ]
}
```

**Error Responses:**
- `400 Bad Request` - File bukan gambar atau format tidak didukung
- `413 Payload Too Large` - File terlalu besar
- `422 Unprocessable Entity` - Gambar tidak dapat diproses

**Catatan Implementasi:**
> ⚠️ **SIMULASI MVP**: Endpoint ini saat ini mengembalikan hasil simulasi untuk testing UI. Pada implementasi final akan menggunakan model AI yang sesungguhnya.

---

## ❌ Error Handling

### Format Error Response

Semua error response mengikuti format standar:

```json
{
  "detail": "Pesan error yang dapat dibaca manusia"
}
```

### HTTP Status Codes

- `200 OK` - Request berhasil
- `201 Created` - Resource berhasil dibuat
- `400 Bad Request` - Request tidak valid
- `401 Unauthorized` - Token tidak valid atau expired
- `403 Forbidden` - Tidak memiliki permission
- `404 Not Found` - Resource tidak ditemukan
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Contoh Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## ⚡ Rate Limiting

**Status:** Belum diimplementasi dalam MVP

**Rencana Implementasi:**
- General API: 100 requests/minute per user
- Upload endpoints: 10 requests/minute per user
- Authentication: 5 requests/minute per IP

---

## 🔧 Development Notes

### Testing dengan cURL

**Login:**
```bash
curl -X POST "http://127.0.0.1:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

**Get Plants:**
```bash
curl -X GET "http://127.0.0.1:8000/plants/" \
  -H "Authorization: Bearer <your_token>"
```

**Upload Image:**
```bash
curl -X POST "http://127.0.0.1:8000/identify" \
  -H "Authorization: Bearer <your_token>" \
  -F "file=@plant_image.jpg"
```

### Database Schema

Untuk informasi lengkap tentang struktur database, lihat:
- `src/backend/models.py` - Model definitions
- `memory-bank/architecture.md` - Database design

---

**Last Updated:** 29 Juni 2025  
**Dokumenter:** AI Dokumenter  
**Version:** 1.0 MVP