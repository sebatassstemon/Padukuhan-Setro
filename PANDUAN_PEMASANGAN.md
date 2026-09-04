# Panduan Pemasangan (untuk tim KKN, sekali saja)

Dokumen ini untuk **orang yang memasang sistem**, bukan untuk pengelola dusun.
Pengelola dusun cukup membaca `PANDUAN_PENGELOLA.md`.

Urutan di bawah harus dijalankan berurutan. Setiap bagian diakhiri cara
memastikan langkahnya benar-benar berhasil sebelum lanjut.

---

## Ringkasan cara kerjanya

```
Pengelola buka  situs.vercel.app/admin
  -> klik "Sign In with GitHub", isi formulir seperti Google Form
  -> klik "Publish"
  -> Sveltia CMS menyimpan perubahan sebagai commit baru di GitHub
  -> Vercel melihat ada commit baru, membangun ulang, lalu menerbitkan
  -> situs berubah. Pengelola tidak pernah melihat kode.
```

Isi situs tersimpan di berkas `content/*.json`. `index.html` membacanya lewat
`fetch()` saat halaman dibuka.

---

## 1. Repo GitHub — SUDAH SELESAI

Repo sudah dibuat, seluruh berkas sudah di-commit, dan sudah dikirim ke
<https://github.com/sebatassstemon/Padukuhan-Setro> pada branch `main`.

Sudah diperiksa: **tidak ada berkas Excel/CSV di dalam repo maupun di
riwayatnya.** `DATA_FINAL_WEBSITE_PADUKUHAN_SETRO.xlsx` berisi NIK, nomor HP,
dan omzet per keluarga, dan sudah dikecualikan lewat `.gitignore`. Jangan
sekali-kali memaksa memasukkannya (`git add -f`) — menghapusnya di commit
berikutnya tidak cukup, riwayatnya harus dibersihkan.

Untuk mengirim perubahan berikutnya dari komputer ini:

```bash
git push
```

Atau lewat VS Code: ikon **Source Control** di bilah kiri, lalu
**Sync Changes**. Komputer ini sudah terautentikasi sebagai pemilik repo.

---

## 2. Menyambungkan ke Vercel

Anda tidak perlu memberikan apa pun dari akun Vercel kepada siapa pun.

1. Masuk ke <https://vercel.com> dengan akun Anda.
2. **Add New → Project**.
3. Pada daftar repo GitHub, pilih **Padukuhan-Setro**, klik **Import**.
   Bila repo tidak muncul, klik **Adjust GitHub App Permissions** dan beri
   Vercel akses ke repo itu.
4. Di layar konfigurasi:
   - **Framework Preset:** `Other`
   - **Root Directory:** biarkan kosong (akar repo)
   - **Build Command:** biarkan kosong
   - **Output Directory:** biarkan kosong
   Situs ini statis tanpa proses build, jadi ketiganya memang harus kosong.
5. Klik **Deploy**, tunggu sampai selesai.

Catat alamat yang diberikan Vercel, misal `padukuhan-setro.vercel.app`.
Alamat ini dibutuhkan di langkah 3.

**Cara memastikan berhasil:** buka alamat itu — situs harus tampil lengkap,
dan `alamat-anda.vercel.app/content/wilayah.json` harus menampilkan data JSON.

Sejak titik ini, setiap commit baru ke branch `main` akan otomatis diterbitkan
ulang oleh Vercel.

---

## 3. Memasang login GitHub untuk pengelola

Tanpa langkah ini, masuk ke `/admin` hanya bisa lewat token GitHub yang harus
dibuat sendiri oleh pengelola — terlalu berat untuk warga yang tidak paham
coding. Langkah ini membuat pengelola cukup menekan satu tombol
**"Sign In with GitHub"**.

Butuh akun Cloudflare (gratis).

### 3a. Pasang Worker

1. Buka <https://github.com/sveltia/sveltia-cms-auth>.
2. Klik tombol **Deploy to Cloudflare Workers** di halaman itu.
3. Izinkan GitHub mengakses Cloudflare, lalu ikuti proses deploy sampai selesai.
4. Browser akan kembali ke GitHub. Buka <https://dash.cloudflare.com> untuk melihat Worker yang baru dibuat.
5. Di dashboard Cloudflare, klik menu **Workers & Pages** di kiri.
6. Catat nama Worker terbaru (biasanya `sveltia-cms-auth`), lalu klik nama itu.
7. Di halaman detail Worker, lihat **Deployments** atau URL yang ditampilkan, bentuknya:
   ```
   https://sveltia-cms-auth.NAMA-ANDA.workers.dev
   ```
   Ganti `NAMA-ANDA` dengan nama subdomain Anda di Cloudflare. Catat alamat lengkapnya.

### 3b. Daftarkan OAuth App di GitHub

1. Buka <https://github.com/settings/developers> → **OAuth Apps** →
   **New OAuth App**.
2. Isi form dengan:
   - **Application name:** bebas, misalnya `Pengelola Situs Padukuhan Setro`
   - **Homepage URL:** bebas, misalnya `https://github.com/sveltia/sveltia-cms-auth`
   - **Authorization callback URL:** **HARUS PERSIS** alamat Worker + `/callback`,
     misalnya `https://sveltia-cms-auth.westprogg220.workers.dev/callback`
     
     ⚠️ Yang dua kolom pertama bisa berisi apa saja, tapi **callback URL harus sesuai
     dengan Worker Anda yang sebenarnya**.

3. Klik **Register application**.
4. Catat **Client ID** (64 karakter heksadesimal).
5. Klik **Generate a new client secret** dan catat **Client Secret** itu.
   Secret hanya ditampilkan sekali — jangan lupa catat.

### 3c. Isi pengaturan Worker

Di dashboard Cloudflare, buka Worker `sveltia-cms-auth` → **Settings** →
**Variables**, lalu tambahkan variabel lingkungan berikut:

**Wajib diisi:**

| Nama | Isi |
|---|---|
| `GITHUB_CLIENT_ID` | Client ID dari langkah 3b |
| `GITHUB_CLIENT_SECRET` | Client Secret dari langkah 3b — klik **Encrypt** |

**Opsional tapi sangat disarankan:**

| Nama | Isi |
|---|---|
| `ALLOWED_DOMAINS` | Nama host situs Anda, misal `padukuhan-setro.vercel.app` |

`ALLOWED_DOMAINS` mencegah orang lain memakai Worker Anda (anti-abuse).
Meskipun opsional, sebaiknya diisi.

Setelah selesai, klik **Deploy** atau **Save and Deploy**.

### 3d. Sambungkan ke CMS

Buka `admin/config.yml`, cari bagian ini di dekat atas berkas:

```yaml
  # base_url: https://GANTI-DENGAN-ALAMAT-WORKER.workers.dev
```

Hapus tanda pagar di depannya dan ganti alamatnya, sehingga menjadi:

```yaml
  base_url: https://sveltia-cms-auth.nama-anda.workers.dev
```

Simpan, commit, lalu push. Vercel akan menerbitkan ulang secara otomatis.

**Cara memastikan berhasil:** buka `alamat-situs-anda.vercel.app/admin`, klik
**Sign In with GitHub**. Harus muncul halaman izin GitHub, lalu Anda masuk ke
dasbor CMS. Bila yang muncul pesan galat, hampir selalu penyebabnya salah satu
dari: callback URL tidak sama persis dengan alamat Worker + `/callback`, atau
`ALLOWED_DOMAINS` tidak sama dengan host situs.

---

## 4. Memberi akses ke pengelola dusun

Pengelola harus punya akun GitHub, dan akun itu harus punya izin tulis ke repo.

1. Buka repo di GitHub → **Settings** → **Collaborators and teams**.
2. **Add people**, masukkan nama akun GitHub pengelola.
3. Beri peran **Write**. Jangan **Admin** — peran Write sudah cukup untuk
   mengedit isi situs, dan lebih aman.
4. Pengelola menerima undangan lewat surel dan harus menerimanya.

---

## 5. Uji ujung-ke-ujung sebelum pelatihan

Jalankan ini sendiri dulu, jangan langsung di depan pengelola.

1. Buka `/admin`, masuk dengan GitHub.
2. Pilih **Teks Halaman → Footer**, ubah baris "Disusun oleh ..." menjadi apa
   saja, misal tambahkan kata "UJI".
3. Klik **Save**, lalu **Publish**.
4. Buka repo di GitHub → tab **Commits**. Harus muncul commit baru.
5. Buka dashboard Vercel → **Deployments**. Harus ada deployment baru berjalan.
6. Setelah selesai (biasanya di bawah satu menit), buka situsnya dan gulir ke
   bawah. Baris footer harus sudah berubah.
7. Kembalikan lagi ke tulisan semula lewat CMS.

Bila keenam langkah ini lolos, sistemnya sudah benar-benar berjalan.

---

## 6. Menguji tanpa internet (opsional)

Sveltia CMS punya mode repositori lokal. Buka `/admin` di Chrome atau Edge,
klik **Work with Local Repository**, lalu pilih folder proyek ini. Perubahan
langsung menulis ke berkas `content/*.json` di komputer, tanpa menyentuh
GitHub. Berguna untuk latihan.

---

## Catatan pemeliharaan

- **Sveltia CMS masih berstatus beta** dan `admin/index.html` memuat versi
  terbaru dari unpkg. Kalau suatu saat `/admin` tiba-tiba bermasalah padahal
  situsnya normal, kemungkinan ada pembaruan CMS yang mengubah perilaku.
  Situsnya sendiri tidak akan ikut rusak — `/admin` terpisah sepenuhnya dari
  `index.html`.
- **Situs tetap hidup walau `content/` gagal dibaca.** Nilai lama masih
  tertanam di `index.html` sebagai cadangan, dengan batas tunggu 3 detik. Ini
  sudah diuji untuk tiga keadaan: berkas hilang, JSON rusak, dan jaringan
  menggantung.
- **Jangan menghapus folder `content/`.** Situs akan tetap tampil, tetapi semua
  suntingan pengelola hilang dan isinya kembali ke data KKN Unit 220.
- **Data pribadi.** Repo ini publik. Jangan pernah memasukkan nomor HP atau NIK
  warga ke berkas JSON mana pun tanpa persetujuan tertulis yang bersangkutan
  (UU 27/2022 tentang Perlindungan Data Pribadi). Kontak di E-Katalog sengaja
  masih `0812-XXXX-XXXX`.
