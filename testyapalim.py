```python
# testyapalim.py - Hesap Makinesi Uygulaması

def hesap_makinesi():
    print("Hesap Makinesi'ne Hoş Geldiniz!")
    print("İşlem Seçenekleri:")
    print("1. Toplama (+)")
    print("2. Çıkarma (-)")
    print("3. Çarpma (*)")
    print("4. Bölme (/)")
    print("5. Üs Alma (**)")
    print("6. Çıkış")

    while True:
        try:
            secim = input("Bir işlem seçin (1/2/3/4/5/6): ")

            if secim == '6':
                print("Hesap makinesi kapatılıyor...")
                break

            if secim not in ('1', '2', '3', '4', '5'):
                print("Geçersiz seçim! Lütfen tekrar deneyin.")
                continue

            sayi1 = float(input("Birinci sayıyı girin: "))
            sayi2 = float(input("İkinci sayıyı girin: "))

            if secim == '1':
                print(f"Sonuç: {sayi1} + {sayi2} = {sayi1 + sayi2}")
            elif secim == '2':
                print(f"Sonuç: {sayi1} - {sayi2} = {sayi1 - sayi2}")
            elif secim == '3':
                print(f"Sonuç: {sayi1} * {sayi2} = {sayi1 * sayi2}")
            elif secim == '4':
                if sayi2 == 0:
                    print("Hata: Sıfıra bölme yapılamaz!")
                    continue
                print(f"Sonuç: {sayi1} / {sayi2} = {sayi1 / sayi2}")
            elif secim == '5':
                print(f"Sonuç: {sayi1} ** {sayi2} = {sayi1 ** sayi2}")

        except ValueError:
            print("Geçersiz sayı girişi! Lütfen sayı giriniz.")

hesap_makinesi()
```