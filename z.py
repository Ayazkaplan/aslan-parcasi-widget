```python
# z.py

import tkinter as tk
import math

class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Sıfıra bölme hatası")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result

    def power(self, a, b):
        result = a ** b
        self.history.append(f"{a} ^ {b} = {result}")
        return result

    def square_root(self, a):
        if a < 0:
            raise ValueError("Negatif sayıların karekökü alınamaz")
        result = math.sqrt(a)
        self.history.append(f"√{a} = {result}")
        return result

def terminal_calculator():
    calc = Calculator()

    print("Hesap Makinesi Uygulaması")
    print("1. Toplama")
    print("2. Çıkarma")
    print("3. Çarpma")
    print("4. Bölme")
    print("5. Üs Alma")
    print("6. Karekök")
    print("7. İşlem Geçmişi")
    print("0. Çıkış")

    while True:
        try:
            secim = input("Seçiminizi yapın (0-7): ")

            if secim == "0":
                print("Çıkış yapılıyor...")
                break

            if secim not in ["1", "2", "3", "4", "5", "6", "7"]:
                print("Geçersiz seçim. Lütfen tekrar deneyin.")
                continue

            if secim == "7":
                print("\nİşlem Geçmişi:")
                for islem in calc.history:
                    print(islem)
                print()
                continue

            if secim in ["1", "2", "3", "4", "5"]:
                sayi1 = float(input("İlk sayıyı girin: "))
                sayi2 = float(input("İkinci sayıyı girin: "))

                if secim == "1":
                    sonuc = calc.add(sayi1, sayi2)
                elif secim == "2":
                    sonuc = calc.subtract(sayi1, sayi2)
                elif secim == "3":
                    sonuc = calc.multiply(sayi1, sayi2)
                elif secim == "4":
                    sonuc = calc.divide(sayi1, sayi2)
                elif secim == "5":
                    sonuc = calc.power(sayi1, sayi2)

                print(f"Sonuç: {sonuc}\n")

            elif secim == "6":
                sayi = float(input("Sayıyı girin: "))
                sonuc = calc.square_root(sayi)
                print(f"Sonuç: {sonuc}\n")

        except ValueError as e:
            print(f"Hata: {e}")
        except Exception as e:
            print(f"Beklenmeyen bir hata oluştu: {e}")

def hesap_makinesi():
    print("Hesaplama modunu seçin:")
    print("1. Terminal Hesap Makinesi")
    print("2. GUI Hesap Makinesi")

    while True:
        secim = input("Seçiminizi yapın (1/2): ")
        if secim == "1":
            terminal_calculator()
            break
        elif secim == "2":
            gui_calculator()
            break
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")

def gui_calculator():
    pencere = tk.Tk()
    pencere.title("Gelişmiş Hesap Makinesi")
    pencere.geometry("400x600")

    calc = Calculator()
    history_window = None

    giris = tk.Entry(pencere, width=20, font=('Arial', 24), borderwidth=2, relief="solid")
    giris.grid(row=0, column=0, columnspan=5, pady=10, padx=10)

    def tus_basimi(tus):
        giris.insert(tk.END, tus)

    def temizle():
        giris.delete(0, tk.END)

    def hesapla():
        try:
            if giris.get().strip() == "":
                return

            sonuc = eval(giris.get())
            giris.delete(0, tk.END)
            giris.insert(0, str(sonuc))

            islem = giris.get() + " = " + str(sonuc)
            calc.history.append(islem)

        except Exception as e:
            giris.delete(0, tk.END)
            giris.insert(0, "Hata!")

    def gecmis_penceresi():
        nonlocal history_window
        if history_window is not None:
            history_window.destroy()

        history_window = tk.Toplevel(pencere)
        history_window.title("İşlem Geçmişi")
        history_window.geometry("300x400")

        scrollbar = tk.Scrollbar(history_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tarih_listesi = tk.Listbox(history_window, yscrollcommand=scrollbar.set, font=('Arial', 12))
        for islem in calc.history[-10:]:
            tarih_listesi.insert(tk.END, islem)

        tarih_listesi.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=tarih_listesi.yview)

    tuslar = [
        ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3), ('√', 1, 4),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3), ('^', 2, 4),
        ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3), ('C', 3, 4),
        ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3), ('H', 4, 4)
    ]

    for (text, row, col) in tuslar:
        if text == '=':
            btn = tk.Button(pencere, text=text, padx=20, pady=20, font=('Arial', 18),
                          command=hesapla)
        elif text == 'C':
            btn = tk.Button(pencere, text=text, padx=20, pady=20, font=('Arial', 18),
                          command=temizle)
        elif text == 'H':
            btn = tk.Button(pencere, text=text, padx=20, pady=20, font=('Arial', 18),
                          command=gecmis_penceresi)
        elif text == '√':
            btn = tk.Button(pencere, text=text, padx=20, pady=20, font=('Arial', 18),
                          command=lambda t=text: tus_basimi('math.sqrt('))
        elif text == '^':
            btn = tk.Button(pencere, text=text, padx=20, pady=20, font=('Arial', 18),
                          command=lambda t=text: tus_basimi('**'))
        else:
            btn = tk.Button(pencere, text=text, padx=20, pady=20, font=('Arial', 18),
                          command=lambda t=text: tus_basimi(t))

        btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

    pencere.grid_columnconfigure(tuple(range(5)), weight=1)
    pencere.grid_rowconfigure(tuple(range(5)), weight=1)

    pencere.mainloop()

if __name__ == "__main__":
    hesap_makinesi()
```