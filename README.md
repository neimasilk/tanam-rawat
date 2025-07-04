# 🌱 Tanam Rawat

**Versi:** 1.0 MVP  
**Status:** 100% Complete - MVP Ready ✅  
**Teknologi:** React Native + FastAPI + PostgreSQL

## 📱 Deskripsi Proyek

Tanam Rawat adalah aplikasi mobile yang membantu pengguna merawat tanaman dengan fitur identifikasi AI, jadwal perawatan, dan komunitas berbagi pengalaman.

## 🚀 Fitur Utama

### ✅ Sudah Diimplementasi
- **Otentikasi Pengguna** - Registrasi dan login dengan JWT
- **Manajemen Tanaman** - CRUD data tanaman dengan informasi lengkap
- **Jadwal Perawatan** - Pengingat penyiraman dan pemupukan
- **Ensiklopedia Hama & Penyakit** - Database lengkap masalah tanaman
- **Forum Komunitas** - Berbagi tips dan pengalaman
- **Identifikasi Tanaman** - Upload foto untuk identifikasi (MVP ready)
- **Keamanan Backend** - Environment variables, file validation, JWT auth

### 🚧 Dalam Pengembangan
- **Model AI Identifikasi** - Integrasi model machine learning
- **Push Notification** - Pengingat otomatis
- **Cloud Storage** - Penyimpanan gambar

## 🛠️ Teknologi Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Otentikasi:** JWT (JSON Web Tokens)
- **Server:** Uvicorn
- **Keamanan:** Environment variables, file validation

### Frontend
- **Framework:** React Native
- **Bahasa:** TypeScript
- **Navigasi:** React Navigation
- **HTTP Client:** Fetch API
- **Image Picker:** React Native Image Picker

### AI & Machine Learning
- **Status:** MVP Simulation (Ready for real model)
- **Target:** TensorFlow/PyTorch model
- **Deployment:** FastAPI model serving

## 📦 Instalasi & Setup

### Prasyarat
- Node.js (v16+)
- Python (v3.8+)
- PostgreSQL (v12+)
- React Native CLI
- Android Studio / Xcode

### Backend Setup

```bash
# Masuk ke direktori backend
cd src/backend

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env dengan kredensial database dan JWT secret

# Setup database PostgreSQL
# Buat database 'tanam_rawat'

# Jalankan server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Setup

```bash
# Masuk ke direktori frontend
cd src/frontend

# Install dependencies
npm install

# Jalankan Metro bundler
npx react-native start

# Jalankan di Android (terminal baru)
npx react-native run-android

# Atau iOS
npx react-native run-ios
```

## 🔗 API Endpoints

### Otentikasi
- `POST /register` - Registrasi pengguna baru
- `POST /token` - Login dan dapatkan access token
- `GET /users/me` - Info pengguna saat ini

### Tanaman
- `GET /plants` - Daftar semua tanaman
- `POST /plants` - Tambah tanaman baru
- `GET /plants/{id}` - Detail tanaman
- `PUT /plants/{id}` - Update tanaman
- `DELETE /plants/{id}` - Hapus tanaman

### Jadwal
- `GET /schedules` - Daftar jadwal perawatan
- `POST /schedules` - Buat jadwal baru
- `PUT /schedules/{id}` - Update jadwal
- `DELETE /schedules/{id}` - Hapus jadwal

### Identifikasi AI
- `POST /identify` - Upload gambar untuk identifikasi (dengan JWT auth)

### Forum Komunitas
- `GET /posts` - Daftar postingan
- `POST /posts` - Buat postingan baru
- `GET /comments` - Daftar komentar
- `POST /comments` - Tambah komentar

## 📊 Status Database

### Tabel Utama
- `users` - Data pengguna dengan password hash
- `plants` - Master data tanaman
- `schedules` - Jadwal perawatan per pengguna
- `pest_diseases` - Ensiklopedia hama & penyakit
- `posts` - Postingan forum komunitas
- `comments` - Komentar pada postingan

## 🔒 Keamanan

### Implementasi Keamanan
- **Environment Variables** - Database credentials dan JWT secret
- **File Upload Validation** - Tipe file dan ukuran (max 10MB)
- **JWT Authentication** - Semua endpoint yang sensitif
- **Temporary File Cleanup** - Automatic cleanup setelah processing
- **Password Hashing** - Bcrypt untuk password storage

### Environment Variables Required
```bash
# Database
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tanam_rawat

# JWT
JWT_SECRET_KEY=your_super_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🧪 Testing

### Backend Testing
```bash
# Test API endpoints dengan curl
curl -X GET http://127.0.0.1:8000/

# Test dengan Postman
# Import collection dari test_scripts/
```

### Frontend Testing
```bash
# Run tests
npm test

# Run dengan coverage
npm run test:coverage
```

## 📁 Struktur Proyek

```
tanam-rawat/
├── src/
│   ├── backend/          # FastAPI backend
│   │   ├── main.py       # Entry point & routes
│   │   ├── models.py     # Database models
│   │   ├── schemas.py    # Pydantic schemas
│   │   ├── auth.py       # Authentication logic
│   │   ├── database.py   # Database connection
│   │   └── .env.example  # Environment template
│   ├── frontend/         # React Native app
│   │   ├── screens/      # App screens
│   │   ├── App.tsx       # Main app component
│   │   └── package.json  # Dependencies
│   └── ai_model/         # Future AI implementation
├── memory-bank/          # Project documentation
├── baby-steps-archive/   # Development history
├── vibe-guide/          # Development guidelines
└── test_scripts/        # Testing utilities
```

## 🔧 Development Workflow

Proyek ini menggunakan **Vibe Coding V1.4** methodology dengan tim hibrida AI-Human.

### Tim Pengembang
- **Arsitek:** Perencanaan dan desain sistem
- **Dokumenter:** Dokumentasi dan komentar kode
- **Developer Backend:** Implementasi API
- **Developer Frontend:** Implementasi UI/UX
- **Tester:** Quality assurance

### Baby-Step Development
Setiap fitur dikembangkan dalam "baby-steps" kecil dengan:
- Tujuan yang jelas
- Tugas spesifik dengan assignee
- Kriteria testing
- Dokumentasi progress

## 🐛 Troubleshooting

### Backend Issues
```bash
# Jika server tidak bisa start
# Pastikan PostgreSQL running
# Check port 8000 tidak digunakan
# Pastikan .env file sudah dikonfigurasi

# Reset database
# Drop dan create ulang database 'tanam_rawat'
```

### Frontend Issues
```bash
# Clear cache
npx react-native start --reset-cache

# Rebuild
cd android && ./gradlew clean && cd ..
npx react-native run-android
```

## 📈 Roadmap

### Phase 1 (Current - MVP) ✅
- ✅ Basic CRUD operations
- ✅ User authentication
- ✅ Community features
- ✅ AI identification (simulation)
- ✅ Security implementation

### Phase 2 (Next)
- 🔄 Real AI model integration
- 🔄 Push notifications
- 🔄 Cloud storage
- 🔄 Advanced scheduling

### Phase 3 (Future)
- 🔄 Social features
- 🔄 Marketplace integration
- 🔄 IoT sensor integration
- 🔄 Multi-language support

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Follow Vibe Coding guidelines
4. Submit pull request
5. Update documentation

## 📄 License

MIT License - See LICENSE file for details

## 📞 Support

Untuk pertanyaan dan dukungan:
- Baca dokumentasi di `memory-bank/`
- Check troubleshooting guide
- Create issue di repository

---

**Last Updated:** 30 Desember 2024  
**Dokumenter:** AI Dokumenter  
**Version:** 1.0 MVP