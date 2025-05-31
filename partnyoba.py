import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont
import datetime
import json
import os

barang_data = {}
keranjang = []
DATA_FILE = "barang_data.json"

def simpan_data():
    with open(DATA_FILE, "w") as f:
        json.dump(barang_data, f, indent=4)

def muat_data():
    global barang_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                barang_data = json.load(f)
            except json.JSONDecodeError:
                barang_data = {}
    else:
        barang_data = {}

def tambah_barang():
    id_barang = entry_id.get().strip()
    id_barang = entry_id.get().strip()
    nama = entry_nama.get().strip()
    harga = entry_harga.get().strip()
    stok = entry_stok.get().strip()
    if not id_barang or not nama or not harga or not stok:
        messagebox.showwarning("Input Kosong", "Semua field harus diisi!")
        return

    if id_barang in barang_data:
        messagebox.showerror("Gagal", "ID barang sudah ada!")
        return

    try:
        barang_data[id_barang] = {
            "nama": nama,
            "harga": int(harga),
            "stok": int(stok)
        }
        simpan_data() 
        messagebox.showinfo("Sukses", f"Barang '{nama}' berhasil ditambahkan.")
        clear_input_fields()
        tampilkan_stok()
        update_listbox()
    except ValueError:
        messagebox.showerror("Error", "Harga dan stok harus berupa angka!")
    except ValueError:
        messagebox.showerror("Error", "Harga dan stok harus berupa angka!")

def clear_input_fields():
    entry_id.delete(0, tk.END)
    entry_nama.delete(0, tk.END)
    entry_harga.delete(0, tk.END)
    entry_stok.delete(0, tk.END)

def update_listbox():
    listbox_id.delete(0, tk.END)
    for id_brg, data in barang_data.items():
        nama = data['nama']
        harga = f"Rp{data['harga']:,}"
        listbox_id.insert(tk.END, f"{ id_brg } - { nama }  { harga }")

def get_selected_id():
    try:
        selected = listbox_id.get(listbox_id.curselection())
        id_barang = selected.split(" - ")[0]  # Ambil hanya bagian ID
        return id_barang
    except IndexError:
        return None

def update_stok_barang():
    id_barang = id_barang.strip()
    stok_baru = stok_baru.strip()

    if not id_barang or not stok_baru:
        messagebox.showwarning("Input Kosong", "ID dan Stok harus diisi!")
        return

    if id_barang not in barang_data:
        messagebox.showerror("Gagal", "ID barang tidak ditemukan!")
        return

    try:
        barang_data[id_barang]["stok"] = int(stok_baru)
        simpan_data()
        messagebox.showinfo("Sukses", f"Stok barang '{barang_data[id_barang]['nama']}' telah diperbarui.")
        tampilkan_stok()
        update_listbox()
        entry_update_id.delete(0, tk.END)
        entry_update_stok.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Error", "Stok harus berupa angka!")

def hapus_barang(id_barang):
    id_barang = id_barang.strip()

    if not id_barang:
        messagebox.showwarning("Input Kosong", "Masukkan ID barang yang ingin dihapus!")
        return

    if id_barang in barang_data:
        confirm = messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin menghapus barang '{barang_data[id_barang]['nama']}'?")
        if confirm:
            del barang_data[id_barang]
            simpan_data()
            messagebox.showinfo("Berhasil", "Barang telah dihapus.")
            tampilkan_stok()
            update_listbox()
            entry_update_id.delete(0, tk.END)
            entry_update_stok.delete(0, tk.END)
    else:
        messagebox.showerror("Gagal", "ID barang tidak ditemukan.")

def cek_barang():
    id_barang = get_selected_id()
    if id_barang and id_barang in barang_data:
        data = barang_data[id_barang]
        label_hasil.config(
            text=f"""
ID: {id_barang}
Nama: {data['nama']}
Harga: Rp{data['harga']:,}
Stok: {data['stok']}
            """, justify="left")
        entry_jumlah.config(state="normal")
        entry_diskon.config(state="normal")
        btn_tambah_keranjang.config(state="normal")
    else:
        label_hasil.config(text="ID Barang tidak ditemukan.")
        entry_jumlah.config(state="disabled")
        entry_diskon.config(state="disabled")
        btn_tambah_keranjang.config(state="disabled")

def tambah_ke_keranjang():
    id_barang = get_selected_id()
    if id_barang and id_barang in barang_data:
        jumlah = entry_jumlah.get().strip()
        diskon = entry_diskon.get().strip()

        if not jumlah.isdigit():
            messagebox.showwarning("Invalid", "Jumlah harus berupa angka!")
            return
        try:
            diskon = float(diskon)
        except ValueError:
            messagebox.showwarning("Invalid", "Diskon harus berupa angka!")
            return

        jumlah = int(jumlah)
        data = barang_data[id_barang]

        if jumlah > data["stok"]:
            messagebox.showwarning("Stok Kurang", "Stok tidak mencukupi.")
            return

        harga_diskon = data["harga"] * (1 - diskon / 100)

        keranjang.append({
            "id": id_barang,
            "nama": data["nama"],
            "harga": harga_diskon,
            "jumlah": jumlah,
            "total": harga_diskon * jumlah
        })

        barang_data[id_barang]["stok"] -= jumlah
   

        messagebox.showinfo("Ditambahkan", f"{jumlah} x {data['nama']} ditambahkan ke keranjang.")
        entry_jumlah.delete(0, tk.END)
        entry_diskon.delete(0, tk.END)
        label_hasil.config(text="")
        update_ringkasan()
        tampilkan_stok()
        simpan_data()
    else:
        messagebox.showwarning("Gagal", "Barang tidak ditemukan.")

def update_ringkasan():
    ringkasan.delete("1.0", tk.END)
    total = 0
    for item in keranjang:
        ringkasan.insert(tk.END, f"{item['jumlah']} x {item['nama']} - Rp{item['total']:,}\n")
        total += item["total"]
    ringkasan.insert(tk.END, f"\nTotal Belanja: Rp{total:,}")

def cetak_struk():
    if not keranjang:
        messagebox.showwarning("Kosong", "Keranjang belanja kosong!")
        return

    now = datetime.datetime.now()
    tanggal = now.strftime("%Y-%m-%d %H:%M:%S")
    total = sum(item["total"] for item in keranjang)

    struk_text = f"""
===== STRUK BELANJA =====
Waktu: {tanggal}

"""
    for item in keranjang:
        struk_text += f"{item['jumlah']} x {item['nama']} = Rp{item['total']:,}\n"
    struk_text += f"\nTotal: Rp{total:,}\n========================\nTerima kasih!"

    popup = tk.Toplevel(root)
    popup.title("Struk Belanja")
    popup.geometry("300x700")
    text_widget = tk.Text(popup, wrap="word")
    text_widget.insert(tk.END, struk_text)
    text_widget.pack(expand=True, fill="both")

    with open("struk_belanja.txt", "w") as f:
        f.write(struk_text)

    keranjang.clear()
    update_ringkasan()

def tampilkan_stok():
    stok_text.delete("1.0", tk.END)
    if not barang_data:
        stok_text.insert(tk.END, "Belum ada data barang.\n")
    else:
        stok_text.insert(tk.END, f"{'ID':<10}{'Nama':<20}{'Harga':<10}{'Stok':<10}\n")
        stok_text.insert(tk.END, "-" * 50 + "\n")
        for id_barang, data in barang_data.items():
            stok_text.insert(tk.END, f"{id_barang:<10}{data['nama']:<20}Rp{data['harga']:<9,} {data['stok']:<6}\n")

root = tk.Tk()
navbar = tk.Frame(root, bg="#8E1616", height=1000)
navbar.pack(fill="x")
root.title("OCIF GUNSHOP")
root.geometry("1080x720")
root.config(bg="#f0f0f0")

label_nav = tk.Label(navbar, text="OCIF GUNSHOP",font=("Blue Ocean", 30, "bold"), fg="white", bg="#8E1616")
label_nav.pack(pady=10)

main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

kiri_frame = tk.Frame(main_frame, bg="#f0f0f0")
kiri_frame.pack(side="left", fill="both", expand=True)

frame_input = tk.LabelFrame(kiri_frame, text="Input Barang Baru", padx=10, pady=10, bg="#ffffff")
frame_input.pack(padx=10, pady=5, fill="both")

entry_id = tk.Entry(frame_input); entry_nama = tk.Entry(frame_input)
entry_harga = tk.Entry(frame_input); entry_stok = tk.Entry(frame_input); 

for i, (text, entry) in enumerate([
    ("ID Barang", entry_id), 
    ("Nama", entry_nama), 
    ("Harga", entry_harga),
    ("Stok", entry_stok), 
]):
    tk.Label(frame_input, text=text, bg="#ffffff").grid(row=i, column=0, sticky="w")
    entry.grid(row=i, column=1, pady=2)

tk.Button(frame_input, text="Tambah Barang", bg="#8E1616", fg="white", command=tambah_barang)\
    .grid(row=5, column=1, columnspan=2, pady=5)

frame_cek = tk.LabelFrame(kiri_frame, text="Cek & Tambah ke Keranjang", padx=10, pady=10, bg="#ffffff")
frame_cek.pack(padx=10, pady=5, fill="both")

tk.Label(frame_cek, text="Pilih ID Barang:", bg="#ffffff").pack()

listbox_id = tk.Listbox(frame_cek, height=2, width=100, exportselection=False)
listbox_id.bind("<<ListboxSelect>>", lambda e: cek_barang())
listbox_id.pack(pady=5)

btn_cek = tk.Button(frame_cek, text="Cek Barang", bg="#8E1616", fg="white", command=cek_barang)
btn_cek.pack(pady=3)

label_hasil = tk.Label(frame_cek, text="", bg="#ffffff", justify="left")
label_hasil.pack()

frame_jumlah_diskon = tk.Frame(frame_cek, bg="#ffffff")
frame_jumlah_diskon.pack(pady=5)

tk.Label(frame_jumlah_diskon, text="Jumlah:", bg="#ffffff").grid(row=0, column=0)
entry_jumlah = tk.Entry(frame_jumlah_diskon, state="disabled", width=10)
entry_jumlah.grid(row=0, column=1, padx=5)

tk.Label(frame_jumlah_diskon, text="Diskon (%):", bg="#ffffff").grid(row=0, column=2)
entry_diskon = tk.Entry(frame_jumlah_diskon, state="disabled", width=10)
entry_diskon.grid(row=0, column=3, padx=5)

btn_tambah_keranjang = tk.Button(frame_cek, text="Tambah ke Keranjang", state="disabled",
                                  bg="#8E1616", fg="white", command=tambah_ke_keranjang)
btn_tambah_keranjang.pack(pady=5)

frame_ringkasan = tk.LabelFrame(kiri_frame, text="Ringkasan Belanja", padx=10, pady=10, bg="#ffffff")
frame_ringkasan.pack(padx=10, pady=5, fill="both", expand=True)

ringkasan = tk.Text(frame_ringkasan, height=7)
ringkasan.pack()

btn_cetak = tk.Button(frame_ringkasan, text="Cetak Struk", bg="#8E1616", fg="white", command=cetak_struk)
btn_cetak.pack(pady=5)

kanan_frame = tk.Frame(main_frame, bg="#8E1616")
kanan_frame.pack(side="right", fill="y", padx=5)

frame_stok = tk.LabelFrame(kanan_frame, text="Stok Barang", padx=10, pady=10, bg="#ffffff")
frame_stok.pack(fill="both", expand=True)

stok_text = tk.Text(frame_stok, height=50, width=90)
frame_update_hapus = tk.Frame(frame_stok, bg="#ffffff")
frame_update_hapus.pack(pady=10)

tk.Label(frame_update_hapus, text="ID Barang:", bg="#ffffff").grid(row=0, column=0, padx=5)
entry_update_id = tk.Entry(frame_update_hapus, width=10)
entry_update_id.grid(row=0, column=1, padx=5)

tk.Label(frame_update_hapus, text="Stok Baru:", bg="#ffffff").grid(row=0, column=2, padx=5)
entry_update_stok = tk.Entry(frame_update_hapus, width=10)
entry_update_stok.grid(row=0, column=3, padx=5)

btn_update_stok = tk.Button(frame_update_hapus, text="Update Stok", bg="orange", fg="white", command=lambda: update_stok_barang(entry_update_id.get(), entry_update_stok.get()))
btn_update_stok.grid(row=1, column=1, columnspan=2, pady=5)

btn_hapus_barang = tk.Button(frame_update_hapus, text="Hapus Barang", bg="red", fg="white", command=lambda: hapus_barang(entry_update_id.get()))
btn_hapus_barang.grid(row=1, column=3, columnspan=2, pady=5)
stok_text.pack()



muat_data()
update_listbox()
tampilkan_stok()
root.mainloop()
