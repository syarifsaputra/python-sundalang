# CHANGELOG v3 - Perubahan Kata Kunci (Keyword)

Lanjutan dari `CHANGELOG.md` (v2). Bagian ini mencatat perubahan kata
kunci bahasa SundaLang yang diminta setelah v2.

## Tabel pemetaan kata kunci: v2 -> v3

| Fungsi                          | Keyword v2 (lama) | Keyword v3 (baru) |
|----------------------------------|---------------------|----------------------|
| Mulai program                   | `Mimiti`            | `mimiti`             |
| **Akhir program**               | `anggeus`           | **`tungtungna`**     |
| Print / cetak                   | `Tingalikeun`       | `tingalikeun`        |
| If                               | `Upami`             | `upami`               |
| Else                             | `lamun_hente`       | `lamun_hente` (tetap)|
| **While**                       | `salila`            | **`ari`**             |
| **Penutup blok if/while**       | `tungtung`          | **`anggeus`**         |

## ⚠️ Hal paling penting untuk diperhatikan

Kata `anggeus` TIDAK dihapus, tapi **artinya berubah total**:
- Di v2: `anggeus` = penutup PROGRAM (di akhir file).
- Di v3: `anggeus` = penutup BLOK `upami`/`ari` (sama posisinya
  seperti `tungtung` di v2). Penutup program sekarang adalah
  `tungtungna`.

Jadi kalau kamu lihat kode lama yang masih ada `anggeus` di baris
paling akhir file, itu sekarang HARUS diganti `tungtungna`, supaya
tidak tertukar dengan `anggeus` yang menutup blok if/while.

## Contoh program lengkap (v3)

```
mimiti
nilai = 80

upami nilai >= 75
    tingalikeun "Lulus, nilai na:", nilai
lamun_hente
    tingalikeun "Teu lulus, nilai na:", nilai
anggeus

i = 0
ari i < 5
    upami i % 2 == 0
        tingalikeun i, "- genap"
    lamun_hente
        tingalikeun i, "- ganjil"
    anggeus
    i = i + 1
anggeus

tungtungna
```

## Detail teknis perubahan

1. **`src/lexer.py`**
   - Semua keyword di `KEYWORDS` dict diganti jadi lowercase dan
     dipetakan ke nama baru: `mimiti`, `tungtungna`, `tingalikeun`,
     `upami`, `lamun_hente`, `ari`, `anggeus`.
   - Karena keyword sekarang case-sensitive lowercase, menulis
     `Mimiti` (kapital) di source `.sunda` TIDAK lagi dikenali
     sebagai keyword -- ia akan dianggap `IDENTIFIER` biasa, dan
     parser akan melaporkan error "Program harus dimulai dengan kata
     'mimiti'". Ini sudah diuji dan berfungsi seperti yang
     diharapkan.

2. **`src/parser_ast.py`**
   - `parse_program()`: sekarang expect `TokenType.MIMITI` di awal dan
     `TokenType.TUNGTUNGNA` di akhir (bukan `ANGGEUS`).
   - `_parse_if()` dan `_parse_while()`: stop-token dan penutup blok
     berubah dari `TUNGTUNG` menjadi `ANGGEUS`. Method `_parse_while`
     sekarang memanggil `_expect(TokenType.ARI)` (bukan `SALILA`).
   - `_end_statement()`: ditambahkan pengecekan `TUNGTUNGNA` selain
     `ANGGEUS`, supaya baris terakhir sebelum penutup program/blok
     tetap valid tanpa perlu newline tambahan.
   - Grammar BNF di docstring sudah disesuaikan sepenuhnya.

3. **`src/semantic.py`, `src/optimizer.py`**
   - Tidak ada perubahan LOGIKA (keduanya bekerja di level AST node,
     bukan keyword teks mentah), hanya komentar dan pesan log yang
     disesuaikan agar konsisten menyebut `upami`/`tingalikeun`
     lowercase.

4. **`src/codegen.py`, `src/main.py`**
   - Tidak ada perubahan sama sekali -- keduanya sudah generic di
     level AST/Token sejak v2, tidak pernah mengecek string keyword
     secara langsung.

5. **File contoh (`testsunda.txt`, `hitungsunda.txt`,
   `contoh_kondisi.txt`)**
   - Seluruh isi diperbarui memakai kata kunci baru.

## Pengujian yang sudah dilakukan untuk v3

- ✅ `testsunda.txt` (print sederhana) -- jalan normal.
- ✅ `hitungsunda.txt` (aritmatika +,-,*,/) -- jalan normal, hasil sama
  seperti sebelumnya.
- ✅ `contoh_kondisi.txt` (if/else + while + nested if-di-dalam-while)
  -- jalan normal, indentasi Python yang digenerate tetap benar.
- ✅ Nested while-di-dalam-while (2 level) -- diuji terpisah, jalan
  normal, setiap `anggeus` menutup blok yang tepat.
- ✅ Pesan error parser untuk kasus: lupa `anggeus` penutup blok,
  tidak diawali `mimiti`, lupa `tungtungna` -- semua menampilkan
  pesan yang benar dan menyebut keyword baru.
- ✅ Keyword lama berkapital (`Mimiti`) dipastikan TIDAK lagi
  dikenali sebagai keyword (sesuai harapan, karena lexer sekarang
  case-sensitive lowercase).

## Cara menguji ulang sendiri

```bash
cd src
python3 main.py ../testsunda.txt
python3 main.py ../hitungsunda.txt
python3 main.py ../contoh_kondisi.txt --show-gen
```
