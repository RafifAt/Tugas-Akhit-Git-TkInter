import tkinter as tk
from tkinter import messagebox
import json
import os
import datetime

DATA_FILE = "barang_data.json"
barang_data = {}
keranjang = []
penjualan_tercatat = {}


PENJUALAN_FILE = "penjualan_data.json"
penjualan_data = []

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

def simpan_penjualan():
    with open(PENJUALAN_FILE, "w") as f:
        json.dump(penjualan_data, f, indent=4)

def muat_penjualan():
    global penjualan_data
    if os.path.exists(PENJUALAN_FILE):
        with open(PENJUALAN_FILE, "r") as f:
            try:
                penjualan_data = json.load(f)
            except json.JSONDecodeError:
                penjualan_data = []
    else:
        penjualan_data = []

def tampilkan_stok():
    stok_text.delete("1.0", tk.END)
    if not barang_data:
        stok_text.insert(tk.END, "Belum ada data barang.\n")
    else:
        stok_text.insert(tk.END, f"{'ID':<10}{'Nama':<20}{'Harga':<15}{'Stok':<10}\n")
        stok_text.insert(tk.END, "-" * 60 + "\n")
        for id_brg, data in barang_data.items():
            stok_text.insert(tk.END, f"{id_brg:<10}{data['nama']:<20}Rp{data['harga']:<13,}{data['stok']:<10}\n")

def tambah_barang():
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
        clear_input_fields()
        tampilkan_stok()
        update_listbox()
        messagebox.showinfo("Sukses", "Barang berhasil ditambahkan.")
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
        listbox_id.insert(tk.END, f"{id_brg} - {data['nama']} (Rp{data['harga']:,})")

def get_selected_id():
    try:
        selected = listbox_id.get(listbox_id.curselection())
        return selected.split(" - ")[0]
    except IndexError:
        return None

def update_stok_barang():
    id_barang = entry_update_id.get().strip()
    stok_baru = entry_update_stok.get().strip()

    if not id_barang or not stok_baru:
        messagebox.showwarning("Input Kosong", "ID dan stok baru harus diisi.")
        return

    if id_barang not in barang_data:
        messagebox.showerror("Error", "ID barang tidak ditemukan.")
        return

    try:
        barang_data[id_barang]['stok'] = int(stok_baru)
        simpan_data()
        tampilkan_stok()
        update_listbox()
        entry_update_id.delete(0, tk.END)
        entry_update_stok.delete(0, tk.END)
        messagebox.showinfo("Sukses", "Stok berhasil diperbarui.")
    except ValueError:
        messagebox.showerror("Error", "Stok harus berupa angka.")

def tampilkan_penjualan():
    penjualan_text.delete("1.0", tk.END)
    if not penjualan_data:
        penjualan_text.insert(tk.END, "Belum ada data penjualan.\n")
        return

    for idx, transaksi in enumerate(penjualan_data, 1):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for item in transaksi['items']:
            penjualan_text.insert(
                tk.END,
                f" Senjata yang Dibeli : {item['jumlah']} x {item['nama']} = Rp{item['total']:,}\n"
            )
        penjualan_text.insert(tk.END, f" Tanggal Transaksi : {now} \n Jumlah Transaksi: Rp{transaksi['total']:,}\n\n")

def hapus_barang():
    id_barang = entry_update_id.get().strip()
    if not id_barang:
        messagebox.showwarning("Input Kosong", "ID barang harus diisi.")
        return

    if id_barang in barang_data:
        confirm = messagebox.askyesno("Konfirmasi", f"Yakin hapus barang '{barang_data[id_barang]['nama']}'?")
        if confirm:
            del barang_data[id_barang]
            simpan_data()
            tampilkan_stok()
            update_listbox()
            entry_update_id.delete(0, tk.END)
            entry_update_stok.delete(0, tk.END)
            messagebox.showinfo("Sukses", "Barang dihapus.")
    else:
        messagebox.showerror("Gagal", "ID barang tidak ditemukan.")

def cek_barang():
    id_barang = get_selected_id()
    if id_barang and id_barang in barang_data:
        data = barang_data[id_barang]
        label_hasil.config(
            text=f"ID: {id_barang}\nNama: {data['nama']}\nHarga: Rp{data['harga']:,}\nStok: {data['stok']}"
        )
        entry_jumlah.config(state="normal")
        entry_diskon.config(state="normal")
        btn_tambah_keranjang.config(state="normal")
    else:
        label_hasil.config(text="ID barang tidak valid.")
        entry_jumlah.config(state="disabled")
        entry_diskon.config(state="disabled")
        btn_tambah_keranjang.config(state="disabled")

def tambah_ke_keranjang():
    id_barang = get_selected_id()
    if id_barang and id_barang in barang_data:
        try:
            jumlah = int(entry_jumlah.get())
            diskon = float(entry_diskon.get())
        except ValueError:
            messagebox.showwarning("Invalid", "Jumlah dan diskon harus angka!")
            return

        data = barang_data[id_barang]
        if jumlah > data['stok']:
            messagebox.showwarning("Stok Kurang", "Stok tidak cukup.")
            return

        harga_diskon = data["harga"] * (1 - diskon / 100)
        total = harga_diskon * jumlah

        keranjang.append({
            "id": id_barang,
            "nama": data["nama"],
            "jumlah": jumlah,
            "harga": harga_diskon,
            "total": total
        })

        barang_data[id_barang]["stok"] -= jumlah
        simpan_data()
        tampilkan_stok()
        update_ringkasan()
        entry_jumlah.delete(0, tk.END)
        entry_diskon.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Barang tidak valid.")

    penjualan_tercatat[id_barang] = penjualan_tercatat.get(id_barang, 0) + jumlah
    

def update_ringkasan():
    ringkasan.delete("1.0", tk.END)
    total = 0
    for item in keranjang:
        ringkasan.insert(tk.END, f"{item['jumlah']} x {item['nama']} - Rp{item['total']:,}\n")
        total += item["total"]
    ringkasan.insert(tk.END, f"\nTotal Belanja: Rp{total:,}")

def center_text(text, width=32):
    return text.center(width)

def cetak_struk():
    if not keranjang:
        messagebox.showwarning("Kosong", "Keranjang kosong.")
        return

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = sum(item["total"] for item in keranjang)

    # Format struk
    struk = ""
    struk += center_text("OCIF GUNSHOP") + "\n"
    struk += center_text("Always Sharp Deals") + "\n"
    struk += center_text("--- INVOICE ---") + "\n\n"
    
    for item in keranjang:
        nama = item['nama']
        jumlah = item['jumlah']
        harga = item['harga']
        total_item = item['total']
        struk += f"{nama[:22]:22}\n{jumlah} x Rp{harga:,} {'':>5}Rp{total_item:,}\n"

    struk += "\n" + "-" * 32 + "\n"
    struk += f"Total Items: {len(keranjang)}\n"
    struk += f"TOTAL:".ljust(20) + f"Rp{total:,.1f}".rjust(12) + "\n"
    struk += "-" * 32 + "\n"
    struk += f"Waktu: {now}\n\n"
    struk += center_text("JANGAN BUANG STRUK BELANJA") + "\n"
    struk += center_text("OCIF GUNSHOP-MU!") + "\n"
    struk += center_text("urusanocifgunshop.id") + "\n"

    # Popup window ukuran kecil dan center
    popup = tk.Toplevel(root)
    popup.title("Struk Belanja")

    width = 300
    height = 400
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")

    text_area = tk.Text(popup, font=("Courier", 9), wrap="none", padx=5, pady=5)
    text_area.insert(tk.END, struk)
    text_area.config(state="disabled")
    text_area.pack(expand=True, fill="both")

    penjualan_data.append({
        "items": keranjang,
        "total": total
    })

    simpan_penjualan()
    keranjang.clear()
    update_ringkasan()
    tampilkan_penjualan()


root = tk.Tk()
root.title("OCIF GUNSHOP")
root.geometry("1080x720")
root.config(bg="#f0f0f0")

navbar = tk.Frame(root, bg="#8E1616", height=60)
navbar.pack(fill="x")

label_nav = tk.Label(navbar, text="OCIF GUNSHOP", font=("Blue Ocean", 60, "bold"), fg="white", bg="#8E1616")
label_nav.pack(pady=10)

main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill="both", expand=True)

# Frame kiri
kiri = tk.Frame(main_frame, bg="#f0f0f0")
kiri.pack(side="left", fill="both", expand=True, padx=10, pady=10)

frame_input = tk.LabelFrame(kiri, bg="white", bd=2, relief="solid")
frame_input.pack(fill="x", padx=5, pady=5)

judul_input = tk.Label(frame_input, text="Input Data Barang", font=("Courier New", 12, "bold"), bg="white")
judul_input.grid(row=0, column=0, columnspan=2, pady=(5, 10))  # Dipindah pakai grid

entry_id = tk.Entry(frame_input); entry_nama = tk.Entry(frame_input)
entry_harga = tk.Entry(frame_input); entry_stok = tk.Entry(frame_input)


for i, (text, entry) in enumerate([
    ("ID", entry_id), ("Nama", entry_nama),
    ("Harga", entry_harga), ("Stok", entry_stok)
]):
    tk.Label(frame_input, text=text, bg="white").grid(row=i+1, column=0, sticky="w", padx=5)
    entry.grid(row=i+1, column=1, pady=2, padx=5)


tk.Button(
    frame_input, text="Tambah Barang",
    bg="#8E1616", fg="white", command=tambah_barang
).grid(row=5, column=0, columnspan=2, pady=10)

frame_cek = tk.LabelFrame(kiri,bg="white", bd=2, relief="solid")
frame_cek.pack(fill="x", padx=5, pady=5)

judul_cek = tk.Label(frame_cek, text="Pilih Barang", font=("Courier New", 12, "bold"), bg="white")
judul_cek.pack()

listbox_id = tk.Listbox(frame_cek, height=5, width=90)
listbox_id.pack(fill="x", padx=5, pady=5)
listbox_id.bind("<<ListboxSelect>>", lambda e: cek_barang())

label_hasil = tk.Label(frame_cek, text="", bg="white", justify="left")
label_hasil.pack()

entry_jumlah = tk.Entry(frame_cek, state="disabled", width=10)

frame_jumlah_diskon = tk.Frame(frame_cek, bg="#ffffff")
frame_jumlah_diskon.pack(pady=5)

tk.Label(frame_jumlah_diskon, text="Jumlah:", bg="#ffffff").grid(row=0, column=0)
entry_jumlah = tk.Entry(frame_jumlah_diskon, state="disabled", width=10)
entry_jumlah.grid(row=0, column=1, padx=5)

tk.Label(frame_jumlah_diskon, text="Diskon (%):", bg="#ffffff").grid(row=0, column=2)
entry_diskon = tk.Entry(frame_jumlah_diskon, state="disabled", width=10)
entry_diskon.grid(row=0, column=3, padx=5)

btn_tambah_keranjang = tk.Button(frame_cek, text="Tambah ke Keranjang", bg="#8E1616", fg="white", state="disabled", command=tambah_ke_keranjang)
btn_tambah_keranjang.pack(pady=5)



frame_ringkasan = tk.LabelFrame(kiri, bg="white", bd=2, relief="solid")
frame_ringkasan.pack(fill="both", expand=True, padx=5, pady=5)

judul_ringkasan = tk.Label(frame_ringkasan, text="Ringkasan", font=("Courier New", 12, "bold"), bg="white")
judul_ringkasan.pack()

ringkasan = tk.Text(frame_ringkasan, height=20, width=90)
ringkasan.pack(pady=20,expand=True)

tk.Button(frame_ringkasan, text="Cetak Struk", bg="#8E1616", fg="white", command=cetak_struk).pack(pady=5)

# Frame kanan
kanan = tk.Frame(main_frame, bg="#f0f0f0")
kanan.pack(side="right", fill="both", expand=True, padx=10, pady=10)

frame_stok = tk.LabelFrame(kanan, bg="white", bd=2, relief="solid")
frame_stok.pack(fill="both", expand=True, padx=0, pady=0)

judul_stok = tk.Label(frame_stok, text="Stok Barang", font=("Courier New", 12, "bold"), bg="white")
judul_stok.pack()

stok_text = tk.Text(frame_stok, height=20, width=90)
stok_text.pack(pady=20, expand=True)

frame_updel = tk.Frame(frame_stok, bg="white")
frame_updel.pack(pady=10, fill="none")

tk.Label(frame_updel, text="ID Barang:", bg="white").grid(row=0, column=0)
entry_update_id = tk.Entry(frame_updel, width=10)
entry_update_id.grid(row=0, column=1)

tk.Label(frame_updel, text="Stok Baru:", bg="white").grid(row=0, column=2)
entry_update_stok = tk.Entry(frame_updel, width=10)
entry_update_stok.grid(row=0, column=3)

tk.Button(frame_updel, text="Update Stok", bg="orange", fg="white", command=update_stok_barang).grid(row=1, column=1, pady=5)
tk.Button(frame_updel, text="Hapus Barang", bg="red", fg="white", command=hapus_barang).grid(row=1, column=3, pady=5)

label_penjualan = tk.Label(frame_stok, text="Riwayat Penjualan", bg="#ffffff", font=("Courier New", 20, "bold"))
label_penjualan.pack(pady=(0, 0))

penjualan_text = tk.Text(frame_stok, height=50, width=90)
penjualan_text.pack(pady=20,expand=True)

muat_data()
muat_penjualan()
update_listbox()
tampilkan_stok()
tampilkan_penjualan()
root.mainloop()
