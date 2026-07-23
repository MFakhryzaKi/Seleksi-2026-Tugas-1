<h1 align="center">
  <br>
  Muhammad Fakhry Zaki <br>
  13524087
  <br>
  <br>
</h1>

_DISCLAIMER: Di tugas ini, saya melakukan scraping menggunakan API karena baru sadar kalau web yang saya pilih tidak memperbolehkan scraping setelah waktu pemilihan tema sudah berakhir_

## Deskripsi Singkat
Pada tugas Seleksi Lab Basdat Stage 2 ini, saya memilih untuk melakukan scraping web yang berisi data hero-hero yang ada di Game Mobile Legends. Alasan pemilihan tersebut adalah karena game tersebut adalah salah satu game yang sering saya mainkan sehingga saya merasa pembuatan database yang berbasis hal tersebut akan menjadi cukup menarik.

Dari scraping, modeling, dan storing yang dilakukan, RDBMS yang saya buat memiliki 6 buah relasi/tabel. Tabel pertama adalah tabel Hero yang berisi deskripsi umum dari suatu hero. Tabel kedua hingga kelima berturut-turut adalah tabel Hero_Role, Hero_Specialty, Hero_Lane_Recommendation, Hero_Price yang masing-masing tabel berisi nomor urut hero dan role, specialty, lane recommendation, atau price dari hero tersebut. Tabel terakhir adalah tabel yang memiliki atribut paling banyak, yaitu tabel Statistics yang berisi statistik lengkap dari suatu hero. 


## Data Scraping
_Data scraping_ dilakukan dengan menggunakan program python scraper.py. Program ini mengambil data melalui MediaWiki Parse API milik Mobile Legends Fandom. Alur kerja program ini adalah pertama, program membuat sebuah HTTP session kemudian mengambil halaman daftar hero menggunakan API. Setelah itu informasi seperti nama hero, role, specialty, dan lain lain bisa didapatkan dengan melakukan parsing dari HTML yang didapat. Hasil _scrape_ ini kemudian disimpan dalam file list_of_heroes.json. Selanjutnya program melakukan _scraping_ lanjutan dari link yang ada pada masing-masing hero. Link ini mengarah kepada laman spesifik dari suatu hero tertentu. Data dari laman tersebut kemudian diambil dan di-_parse_ juga untuk mendapatkan statistik detail masing-masing hero. Hasil ini disimpan pada file hero_statistics.json. 

## Model ERD dan Relasional
Dari data pada kedua file .json (list_of_heroes dan hero_statistics), saya memodelkan ERD dengan 2 entitas, yakni Hero dan Statistics. Relasi antara keduanya merupakan relasi _one-to-one_ dengan Statistics merupakan weak entitas dari Hero. Pemodelan entitas Statistics sebenarnya masih bisa diletakkan pada entitas Hero, tetapi saya memilih untuk memisahkannya (denormalisasi) karena atributnya yang banyak dan agar memudahkan pemodelan.

![ERD](Data%20Storing/design/ERD.png)

Kemudian model relasional ditranslasikan dari ERD tersebut. Proses translasinya mengubah yang awalnya 2 entitas dan satu relationship menjadi 6 buah relasi. Tabel Hero_Role, Hero_Specialty, Hero_Lane_Recommendation, dan Hero_Price menjadi relasi baru karena merupakan atribut _multivalue_ pada entitas Hero.

![Model Relasional](Data%20Storing/design/Model%20Relasional.png)

## Penggunaan Program

Pada bagian ini, akan dijelaskan bagaimana program dijalankan, mulai dari _scraping_ hingga _storing_. Disarankan untuk menjalankan perintah-perintah ini pada terminal WSL/Linux agar tidak mengalami error. Jalankan masing-masing perintah ini secara berurutan dari folder utama.
1. Melakukan _Scraping_
```
python "Data Scraping/src/scraper.py"
```
Perintah ini akan menghasilkan file .json yang ada pada folder data di folder Data Scraping
2. Membuat Skema Database
```
mysql -u root -p < "Data Storing/src/schema.sql"
```
Setelah perintah ini dijalankan, database MobileLegends akan muncul di RDBMS MariaDB mu. Namun, pada tahap ini, tabel-tabel yang ada belum memiliki isi.
3. Mengisikan Data ke Database
Sebelum memasukkan data menggunakan data_inserter, diperlukan untuk membuat sebuah user baru terlebih dahulu yang memiliki akses ke database MobileLegends yang telah dibuat. Jalankan perintah-perintah ini pada MariaDB.
```
CREATE USER 'data_inserter'@'localhost' IDENTIFIED BY 'password_baru';
GRANT ALL PRIVILEGES ON MobileLegends.* TO 'data_inserter'@'localhost';
FLUSH PRIVILEGES;
```
Bagian 'password_baru' bisa diisi dengan apa pun.

Setelah memiliki user yang bisa mengakses database, pengisian data bisa dilakukan dengan perintah : 
```
python3 "Data Storing/src/data_inserter.py"
```
Masukkan password yang dibuat sebelumnya untuk menjalankan program. Setelah program selesai, database MobileLegends akan berisi data-data Hero di Mobile Legends.

## Referensi
- URL scraping : https://mobile-legends.fandom.com/wiki/List_of_heroes
- Library python :
    - BeautifulSoup (https://beautiful-soup-4.readthedocs.io/en/latest/)
    - pymysql (https://pymysql.readthedocs.io/en/latest/)
- RDBMS : MariaDB (https://mariadb.org/)

## Penggunaan AI
1. Pencarian tentang aturan dan etika data scraping
2. Pembuatan script data scraping 
3. Membantu memberi ide dan debungging penulisan data_inserter dan schema