# Panduan Agent: Membuat Sistem Admin untuk index.html Padukuhan Setro

## Konteks

`index.html` adalah situs statis satu file (~6900 baris) untuk website potensi Padukuhan Setro (KKN UII Unit 220). Tidak ada database, tidak ada backend — dan memang harus tetap begitu. Rencana hosting: GitHub → Vercel (auto-deploy setiap ada commit baru ke branch utama).

**Repo GitHub yang sudah disiapkan owner:** https://github.com/sebatassstemon/Padukuhan-Setro.git — pakai repo ini, jangan buat repo baru. Cek dulu isinya (`git remote -v` setelah clone, atau `gh repo view sebatassstemon/Padukuhan-Setro`) sebelum mulai kerja, karena bisa saja masih kosong atau sudah ada isi awal dari owner.

**Masalah yang harus diselesaikan tugas ini:** admin pengelola situs (warga/perangkat dusun) akan dilatih untuk mengelola situs ini, tapi dia **tidak paham coding sama sekali**. Semua konten saat ini hardcode langsung di HTML/JavaScript. Tugas Anda: pindahkan **seluruh konten yang bukan urusan kode** (angka, teks, foto, daftar) ke sistem yang bisa diedit admin lewat formulir web — bukan lewat edit file.

**Yang TIDAK boleh disentuh:** seluruh CSS, animasi (GSAP/ScrollTrigger/Flip/Lenis/Swiper), struktur layout, JavaScript interaksi (coverflow, kotak yang memuai, carousel). Situs ini dirancang dan dipoles sangat detail — jangan "diperbaiki" atau disederhanakan, hanya disambungkan ke sumber data baru.

**Tidak ada urutan prioritas.** Owner situs ingin SEMUA konten non-kode bisa diedit admin — kerjakan semua section, bukan sebagian.

---

## Arsitektur yang dipakai

**Git-based headless CMS** — rekomendasi: [Sveltia CMS](https://github.com/sveltia/sveltia-cms) (penerus Decap/Netlify CMS, lebih aktif dikembangkan). Alurnya:

```
Admin buka situs.vercel.app/admin
  → login, isi formulir (judul, foto, kontak, dst — seperti Google Form)
  → klik "Publish"
  → Sveltia CMS commit otomatis ke GitHub lewat GitHub API
  → Vercel mendeteksi commit baru di branch utama
  → Vercel build ulang & deploy otomatis
  → Situs live ter-update, admin tidak pernah lihat kode
```

Karena situsnya statis tanpa build step (Tailwind lewat CDN, bukan dikompilasi), konten harus dipindah ke **berkas JSON terpisah** di folder `content/`, lalu `index.html` mengambilnya lewat `fetch()` saat halaman dibuka — bukan lagi ditulis langsung sebagai `const` di dalam `<script>`.

---

## Pola teknis WAJIB — sudah diuji, terbukti tidak merusak situs

Pola ini sudah dicoba langsung di sesi sebelumnya pada 2 koleksi (katalog & kegiatan) dan **dikonfirmasi bekerja tanpa merusak GSAP/Lenis/ScrollTrigger/coverflow yang ada**. Pakai pola persis ini untuk semua koleksi, jangan improvisasi pendekatan lain.

### Langkah A — Ubah `const` jadi `let`
Semua deklarasi array/objek data di bagian `/* ============ DATA ============ */` di dalam `<script>` (dekat akhir `<body>`) diubah dari `const NAMA = [...]` menjadi `let NAMA = [...]`. **Nilai aslinya JANGAN diubah** — ini jadi fallback bawaan kalau nanti fetch gagal.

### Langkah B — Bungkus SELURUH isi `<script>` itu dengan IIFE async
```html
<script>
  (async function () {
    /* ============ DATA ============ */
    let WILAYAH = [ ... ];   // isi asli, tidak berubah
    ... SELURUH kode yang sudah ada, jangan direstrukturisasi ...
  })();
</script>
```
Ini satu-satunya script tag berisi logika di halaman (dicek: tidak ada `onclick=` inline, tidak ada script lain yang mereferensikan variabel-variabel ini). Aman dibungkus penuh.

### Langkah C — Sisipkan pemuat konten, tepat setelah SEMUA `let` data selesai dideklarasikan (sebelum kode pertama yang memakainya)
```js
async function muatKonten(url) {
  try {
    const kontrol = new AbortController();
    const batas = setTimeout(() => kontrol.abort(), 3000); // jangan sampai halaman menggantung kalau jaringan lambat
    const r = await fetch(url, { signal: kontrol.signal });
    clearTimeout(batas);
    return r.ok ? await r.json() : null;
  } catch (e) { return null; }
}
const hasil = await Promise.all([
  muatKonten('content/wilayah.json'),
  muatKonten('content/usia.json'),
  muatKonten('content/kerja.json'),
  // ... satu baris per koleksi, urutan harus sama dengan pengecekan di bawah
]);
if (Array.isArray(hasil[0]) && hasil[0].length) WILAYAH = hasil[0];
if (Array.isArray(hasil[1]) && hasil[1].length) USIA = hasil[1];
if (Array.isArray(hasil[2]) && hasil[2].length) KERJA = hasil[2];
// ... dst
```

**Kenapa polanya begini:** kalau `content/*.json` belum ada, gagal dimuat, atau jaringan lambat, situs TETAP tampil normal memakai data bawaan di kode — tidak pernah blank, tidak pernah menggantung. Ini penting karena hampir seluruh inisialisasi JS di halaman (parallax hero, efek tablet scroll, kotak yang memuai, dst) sekarang berjalan setelah `await` ini — kalau fetch tidak pernah selesai, seluruh halaman ikut mati. Timeout 3 detik + fallback adalah pengaman wajib, jangan dihilangkan.

**Verifikasi setelah tiap perubahan:** jalankan `python screenshot.py http://localhost:3000` atau buka browser ke `localhost:3000` (server sudah menyala di port itu — cek dulu dengan `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000` sebelum menyalakan server baru), cek console tidak ada error, dan cek lewat `document.querySelectorAll(...)` di console browser bahwa jumlah item yang ter-render cocok dengan isi JSON.

---

## Peta konten lengkap

Struktur section di halaman (urutan dari atas): Nav → Hero → Profil Wilayah → Potret Warga (3 kotak) → Potensi Setro (3 kotak) → E-Katalog → Program Kerja → Kegiatan Warga → Kemitraan → Kontak → Footer.

**Catatan penting:** nomor baris di bawah ini KEMUNGKINAN BESAR sudah bergeser sejak dokumen ini ditulis (file terus diedit). **Jangan percaya nomor baris — selalu `grep`/cari ulang lokasi lewat nama variabel atau komentar sebelum edit.**

### Tier A — sudah dalam bentuk array JS bernama, tinggal disambungkan ke fetch (mudah, ikuti pola di atas persis)

| Koleksi | Variabel JS | Bentuk data | Isi field |
|---|---|---|---|
| Wilayah RT/RW | `WILAYAH` | array-of-array | `[nama, KK, jiwa, laki-laki, perempuan, tipe]` |
| Struktur usia | `USIA` | array-of-array | `[nama kelompok, jumlah, keterangan, warna]` |
| Mata pencaharian | `KERJA` | array-of-array | `[nama pekerjaan, jumlah, flag-disorot]` |
| Sumber air | `AIR` | array-of-array | `[nama sumber, jumlah KK]` |
| Komoditas tani | `KOMODITAS` | array-of-array | `[nama komoditas, jumlah KK]` |
| Jenis usaha (potensi) | `UMKM` | array-of-array | `[jenis usaha, jumlah unit]` |
| **E-Katalog UMKM** | `KATALOG` | array-of-object | `judul, sub, unit, desk, foto, kontak, jam, lokasi` |
| Program Kerja | `PROGRAM` | array-of-array | `[bidang, judul, deskripsi, nama berkas panduan]` |
| **Kegiatan Warga** | `KEGIATAN` | array-of-string | judul kegiatan (masih 14 dari 20 dummy — biarkan, admin yang nanti isi/hapus lewat CMS, JANGAN dihapus di tahap ini) |
| Kemitraan | `MITRA` | array-of-array | `[label kebutuhan, jumlah, satuan]` |

Selain array bernama di atas, ada 4 blok statistik yang saat ini ditulis sebagai **array literal langsung di dalam pemanggilan fungsi** `kartuStat([...])` (bukan `const` terpisah) — untuk `infra-stat`, `tani-stat`, `ternak-stat`, `umkm-stat`. Ini juga masuk Tier A secara konsep, tapi harus DULU ditarik keluar jadi variabel `let` bernama (misal `let INFRA_STAT = [...]`) sebelum bisa mengikuti pola fetch yang sama.

### Tier B — teks statis di HTML, BUKAN digerakkan JS sama sekali (perlu instrumentasi tambahan sebelum bisa disambung ke JSON)

Untuk tiap item berikut: beri `id` atau `data-*` attribute pada elemen HTML-nya (kalau belum ada), lalu tambahkan pengisian `.textContent`/`.innerHTML` dari hasil fetch JSON di bagian `muatKonten` yang sama — pola fetch+fallback-nya identik dengan Tier A, cuma target akhirnya beda (isi elemen langsung, bukan re-render lewat fungsi render yang sudah ada).

- **Beranda (Hero):** judul 2 baris, paragraf pembuka, 5 angka statistik + label + catatan bintang, catatan sumber data di bawah strip statistik.
- **6 kotak "Potret Warga" & "Potensi Setro"** (struktur penduduk, mata pencaharian, infrastruktur, pertanian, peternakan, usaha warga): tiap kotak punya angka utama, satu baris keterangan pendek, dan satu paragraf `kotak__lead` yang lebih panjang di bagian yang terbuka.
- **Kemitraan:** paragraf pembuka section (di luar array `MITRA`).
- **Kontak:** alamat, nomor WhatsApp, catatan jam berkunjung.
- **Footer:** alamat singkat, paragraf "Sumber data" (menyebut tanggal survei), baris "Disusun oleh KKN ... Angkatan ..." — baris ini PENTING gampang diedit karena wajib diubah tiap pergantian angkatan KKN.

---

## Urutan kerja yang disarankan

1. **`git init`** di root proyek (belum ada repo lokal sama sekali saat ini), lalu `git remote add origin https://github.com/sebatassstemon/Padukuhan-Setro.git`.
2. **Tanyakan ke owner** (jangan asumsikan): apakah sudah ada akun Vercel yang mau dipakai untuk menyambungkan repo di atas?
3. Buat `.gitignore` yang mengecualikan **`DATA_FINAL_WEBSITE_PADUKUHAN_SETRO.xlsx`** dan file Excel sensus lain — file itu berisi data pribadi warga (NIK/HP/omzet per KK) dan TIDAK BOLEH masuk repo yang akan publik. Ini bukan opsional.
4. Ekstrak seluruh Tier A ke `content/*.json`, satu file per koleksi, terapkan pola fetch di atas. Uji tiap koleksi selesai diekstrak (jangan tunggu semua selesai baru diuji sekali).
5. Lanjutkan ke Tier B satu per satu, dengan cara yang sama.
6. Sambungkan repo ke GitHub, sambungkan repo itu ke Vercel (auto-deploy dari branch utama).
7. Pasang Sveltia CMS: buat `/admin/index.html` + `/admin/config.yml` yang mendefinisikan field per koleksi sesuai peta konten di atas — field admin harus pakai label Bahasa Indonesia yang jelas (bukan nama variabel teknis seperti `KATALOG`), dan untuk field foto pakai widget upload gambar, bukan isi path manual.
8. Untuk autentikasi Sveltia CMS ke GitHub: **cek dokumentasi resmi Sveltia CMS versi terbaru saat mengerjakan** (bukan diasumsikan dari pengetahuan lama) — mekanismenya bisa berubah, dan salah pasang auth adalah titik gagal paling umum di setup CMS git-based.
9. Uji end-to-end: login admin dummy → ubah satu field → publish → pastikan commit muncul di GitHub → pastikan Vercel re-deploy otomatis → pastikan situs live berubah.
10. Setelah sistem terbukti jalan, siapkan materi pelatihan admin (idealnya rekaman layar tiap langkah, bukan cuma dokumen tertulis).

## Rambu keamanan

- Jangan pernah commit file Excel data mentah warga ke repo.
- Repo akan publik (supaya angkatan KKN berikutnya bisa lanjut tanpa akses akun pribadi) — pastikan tidak ada nomor HP/NIK warga individual yang ikut ter-commit di JSON manapun. Katalog UMKM saat ini sengaja masih pakai kontak placeholder (`0812-XXXX-XXXX`) sampai ada persetujuan tertulis pelaku usaha — pertahankan itu, jangan diisi nomor asli tanpa instruksi eksplisit dari owner.
