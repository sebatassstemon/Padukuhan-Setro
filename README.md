# Situs Potensi Padukuhan Setro

Situs profil dan potensi Padukuhan Setro, Kalurahan Kulur, Kapanewon Temon,
Kabupaten Kulon Progo, DIY. Disusun oleh KKN Universitas Islam Indonesia
Unit 220.

**Situs statis satu berkas, tanpa basis data dan tanpa proses build.**
Seluruh isinya bisa diubah lewat formulir di `/admin` tanpa menyentuh kode.

## Mau berbuat apa?

| Kebutuhan | Baca |
|---|---|
| Mengubah isi situs (angka, teks, foto) | [PANDUAN_PENGELOLA.md](PANDUAN_PENGELOLA.md) |
| Memasang sistemnya dari nol | [PANDUAN_PEMASANGAN.md](PANDUAN_PEMASANGAN.md) |

## Isi folder

```
index.html            seluruh situs: HTML, CSS, dan JavaScript dalam satu berkas
content/              isi situs dalam bentuk JSON — inilah yang diedit lewat /admin
admin/                Sveltia CMS: index.html + config.yml
assets/               logo, video latar, foto hero
assets/unggahan/      foto yang diunggah pengelola lewat /admin
foto produk dummy/    foto contoh untuk E-Katalog
brand_assets/         panduan merek dan logo asli
vercel.json           pengaturan header untuk Vercel
screenshot.py         alat bantu pengembangan (Playwright)
```

## Cara isinya sampai ke halaman

`index.html` memuat seluruh berkas `content/*.json` lewat `fetch()` saat halaman
dibuka, lalu menimpa nilai bawaan yang tertanam di dalam kode.

Nilai bawaan itu **sengaja dipertahankan sebagai cadangan**. Bila `content/`
tidak terbaca — berkas hilang, JSON rusak, atau jaringan menggantung — situs
tetap tampil utuh memakai data KKN Unit 220. Ada batas tunggu 3 detik supaya
halaman tidak pernah menggantung. Ketiga keadaan itu sudah diuji.

Karena itu: **kalau menambah data baru ke `content/`, jangan menghapus nilai
bawaan di `index.html`.**

## Menjalankan secara lokal

```bash
python -m http.server 3000
```

Lalu buka <http://localhost:3000>. Halaman pengelola ada di
<http://localhost:3000/admin> — pilih **Work with Local Repository** untuk
menyunting berkas `content/` langsung di komputer tanpa menyentuh GitHub.

## Data pribadi

Repo ini publik. Berkas Excel hasil sensus warga (berisi NIK, nomor HP, dan
omzet per keluarga) **tidak boleh masuk repo** dan sudah dikecualikan lewat
`.gitignore`.

Nomor kontak pada E-Katalog sengaja masih berupa `0812-XXXX-XXXX` sampai ada
persetujuan tertulis dari masing-masing pelaku usaha (UU 27/2022 tentang
Perlindungan Data Pribadi).
