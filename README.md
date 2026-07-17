# Finger Volume Control 🖐️🔊

Kontrol volume Windows menggunakan **jumlah jari yang terangkat**, dideteksi
secara real-time lewat kamera dengan **MediaPipe Hands**. Setiap jari yang
terangkat merepresentasikan **10% volume** — angkat 10 jari (dua tangan) untuk
volume 100%, kepal tangan (0 jari) untuk volume 0%.

## Cara Kerja
1. Kamera menangkap gambar tangan secara real-time.
2. **MediaPipe Hands** mendeteksi 21 titik landmark per tangan (hingga 2 tangan).
3. Untuk 4 jari (telunjuk, tengah, manis, kelingking): jari dianggap terangkat
   jika ujung jari (*tip*) lebih tinggi (nilai `y` lebih kecil) dibanding sendi
   dua ruas di bawahnya (*pip*).
4. Untuk jempol: dideteksi berdasarkan posisi horizontal (`x`), karena gerakan
   jempol condong menyamping, bukan naik-turun.
5. Total jari dari kedua tangan dijumlahkan (maksimum 10), lalu dikonversi
   menjadi persentase volume (`jumlah_jari / 10`).
6. Volume sistem Windows diubah langsung lewat **pycaw** (wrapper Python untuk
   Windows Core Audio API).

## Demo Perilaku
| Jari Terangkat | Volume |
|---|---|
| 0 (kepalan tangan) | 0% |
| 3 | 30% |
| 5 (satu tangan terbuka penuh) | 50% |
| 8 | 80% |
| 10 (dua tangan terbuka penuh) | 100% |

## Struktur Repository
```
finger-volume-control/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
└── src/
    └── volume_control.py
```

## ⚠️ Persyaratan Sistem
- **Windows only** — karena menggunakan `pycaw`/`comtypes` untuk mengakses
  Windows Core Audio API secara langsung. Untuk macOS/Linux, bagian kontrol
  volume perlu diganti (misalnya `osascript` di macOS, atau `amixer`/`pactl`
  di Linux — lihat bagian **Pengembangan Lanjutan** di bawah).
- Python 3.9 – 3.11 direkomendasikan (MediaPipe belum selalu stabil di versi
  Python terbaru).
- Webcam yang berfungsi.

## Instalasi

```bash
python -m venv venv
venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

## Menjalankan
```bash
python src/volume_control.py
```

- Jendela kamera akan terbuka menampilkan kerangka tangan (titik biru, garis putih).
- Jumlah jari & persentase volume ditampilkan di pojok kiri atas layar.
- Tekan **`q`** untuk keluar.

## Detail Teknis: Landmark MediaPipe Hands
MediaPipe Hands mendeteksi 21 titik per tangan. Titik yang dipakai di sini:

| Landmark ID | Bagian |
|---|---|
| 4 | Ujung jempol |
| 3 | Ruas jempol (IP) |
| 8 | Ujung telunjuk |
| 6 | Ruas telunjuk (PIP) |
| 12 | Ujung jari tengah |
| 10 | Ruas jari tengah (PIP) |
| 16 | Ujung jari manis |
| 14 | Ruas jari manis (PIP) |
| 20 | Ujung kelingking |
| 18 | Ruas kelingking (PIP) |

## Troubleshooting

**Kamera tidak terbuka / `cap.isOpened()` False**
- Pastikan tidak ada aplikasi lain yang sedang memakai kamera.
- Coba ganti index kamera: `cv2.VideoCapture(1, cv2.CAP_DSHOW)` kalau `0` tidak berhasil.

**`ModuleNotFoundError: No module named 'pycaw'` atau `comtypes`**
- Pastikan sudah menjalankan `pip install -r requirements.txt` di environment yang aktif.

**Volume tidak berubah sama sekali**
- Pastikan menjalankan script di Windows (bukan WSL/macOS/Linux).
- Coba jalankan terminal sebagai Administrator jika ada masalah permission ke Core Audio API.

**Deteksi jempol terbalik / kurang akurat**
- Karena gambar di-flip (efek cermin), logika kiri/kanan jempol disesuaikan
  berdasarkan label tangan (`Left`/`Right`) dari MediaPipe. Jika mendeteksi
  jempol dengan tangan yang salah orientasi (jauh dari kamera/miring), coba
  posisikan tangan lebih tegak menghadap kamera.

## Pengembangan Lanjutan
- **Smoothing volume**: tambahkan filter (misalnya rata-rata beberapa frame
  terakhir) agar transisi volume tidak "melompat-lompat" akibat deteksi yang
  goyah.
- **Dukungan macOS/Linux**: ganti bagian kontrol audio dengan:
  - macOS: `osascript -e "set volume output volume {persen}"`
  - Linux: `amixer set Master {persen}%` atau `pactl set-sink-volume`
- **Gesture tambahan**: misalnya kepalan tangan cepat 2x untuk mute/unmute.
- **Tampilan volume bar**: gambar progress bar visual di layar (bukan cuma teks).
- **Kalibrasi sensitivitas**: sesuaikan `min_detection_confidence` /
  `min_tracking_confidence` sesuai kondisi pencahayaan ruangan.

## Lisensi
Lihat file [LICENSE](LICENSE).
