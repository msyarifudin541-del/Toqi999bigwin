# Toqi99bigwin - Blackjack Simulator

A web-based Blackjack game built with Python (Flask).

## 1. Prerequisites / Syarat
Make sure you have **Python** installed on your computer.
Pastikan **Python** sudah terinstall di komputer Anda.

## 2. Installation / Cara Install
Open your terminal or command prompt in this folder and run:
Buka terminal atau command prompt di folder ini dan jalankan:

```bash
pip install -r requirements.txt
```

**Note for VS Code users:**
If you see yellow warnings like "Import 'flask' could not be resolved", it means your editor is not using the correct Python environment where you installed the packages.
1. Press `Ctrl + Shift + P`.
2. Type "Python: Select Interpreter".
3. Select the environment marked as (Global) or (venv) where you ran the pip install command.
4. Restart VS Code if necessary.

**Catatan untuk pengguna VS Code:**
Jika Anda melihat peringatan kuning seperti "Import 'flask' could not be resolved", itu berarti editor Anda tidak menggunakan environment Python yang benar.
1. Tekan `Ctrl + Shift + P`.
2. Ketik "Python: Select Interpreter".
3. Pilih environment di mana Anda menjalankan perintah pip install tadi.

## 3. How to Run / Cara Menjalankan
Run the following command:
Jalankan perintah berikut:

```bash
python app.py
```

Then open your browser and go to:
Lalu buka browser dan kunjungi:
`http://127.0.0.1:5000`

## Features
- **Register & Login**: Create your account.
- **Deposit**: Add virtual money to your wallet.
- **Blackjack**: Play against the dealer.
    - Hit (Tambah kartu)
    - Stand (Tahan)
    - Dealer stands on 17.

## Disclaimer
This is a learning project for educational purposes only.
Ini adalah proyek pembelajaran untuk tujuan edukasi saja.
