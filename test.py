İşte temizlenmiş ve düzeltilmiş Python kodu:

```python
"""test.py - VX - Gelişmiş Hesap Makinesi"""

import math
import re
from typing import Union, List, Tuple, Optional
from decimal import Decimal, getcontext

print("Merhaba VX!")

class AdvancedCalculator:
    """Gelişmiş hesap makinesi sınıfı.

    Desteklenen işlemler:
    - Temel aritmetik işlemler (+, -, *, /, ^)
    - Trigonometrik fonksiyonlar (sin, cos, tan, asin, acos, atan)
    - Logaritmik fonksiyonlar (log, ln)
    - Üslü sayı hesaplama
    - Kök alma
    - Faktöriyel hesaplama
    - Mod alma
    - Yüzde hesaplama
    - Bellek fonksiyonları (M+, M-, MR, MC)
    - Geçmiş kaydı
    """

    def __init__(self):
        """Hesap makinesi başlatıcı."""
        self.memory: Decimal = Decimal('0')
        self.history: List[Tuple[str, Decimal]] = []
        getcontext().prec = 28  # Yüksek hassasiyetli hesaplama için

    def _validate_input(self, value: Union[int, float, str, Decimal]) -> Decimal:
        """Giriş değerini Decimal'a dönüştürür ve doğrular."""
        try:
            if isinstance(value, Decimal):
                return value
            return Decimal(str(value))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Geçersiz giriş değeri: {value}") from e

    def _add_to_history(self, operation: str, result: Decimal) -> None:
        """İşlemi geçmişe ekler."""
        self.history.append((operation, result))

    def add(self, a: Union[int, float, str, Decimal], b: Union[int, float, str, Decimal]) -> Decimal:
        """Toplama işlemi."""
        a_dec = self._validate_input(a)
        b_dec = self._validate_input(b)
        result = a_dec + b_dec
        self._add_to_history(f"{a} + {b}", result)
        return result

    def subtract(self, a: Union[int, float, str, Decimal], b: Union[int, float, str, Decimal]) -> Decimal:
        """Çıkarma işlemi."""
        a_dec = self._validate_input(a)
        b_dec = self._validate_input(b)
        result = a_dec - b_dec
        self._add_to_history(f"{a} - {b}", result)
        return result

    def multiply(self, a: Union[int, float, str, Decimal], b: Union[int, float, str, Decimal]) -> Decimal:
        """Çarpma işlemi."""
        a_dec = self._validate_input(a)
        b_dec = self._validate_input(b)
        result = a_dec * b_dec
        self._add_to_history(f"{a} * {b}", result)
        return result

    def divide(self, a: Union[int, float, str, Decimal], b: Union[int, float, str, Decimal]) -> Decimal:
        """Bölme işlemi."""
        a_dec = self._validate_input(a)
        b_dec = self._validate_input(b)
        if b_dec == 0:
            raise ZeroDivisionError("Sıfıra bölme hatası")
        result = a_dec / b_dec
        self._add_to_history(f"{a} / {b}", result)
        return result

    def power(self, base: Union[int, float, str, Decimal], exponent: Union[int, float, str, Decimal]) -> Decimal:
        """Üslü sayı hesaplama."""
        base_dec = self._validate_input(base)
        exponent_dec = self._validate_input(exponent)
        result = base_dec ** exponent_dec
        self._add_to_history(f"{base}^{exponent}", result)
        return result

    def sqrt(self, value: Union[int, float, str, Decimal]) -> Decimal:
        """Karekök alma."""
        value_dec = self._validate_input(value)
        if value_dec < 0:
            raise ValueError("Negatif sayıların karekökü alınamaz")
        result = value_dec.sqrt()
        self._add_to_history(f"√{value}", result)
        return result

    def factorial(self, n: Union[int, float, str, Decimal]) -> Decimal:
        """Faktöriyel hesaplama."""
        n_int = int(self._validate_input(n))
        if n_int < 0:
            raise ValueError("Negatif sayıların faktöriyeli alınamaz")
        result = Decimal(math.factorial(n_int))
        self._add_to_history(f"{n}!", result)
        return result

    def mod(self, a: Union[int, float, str, Decimal], b: Union[int, float, str, Decimal]) -> Decimal:
        """Mod alma işlemi."""
        a_dec = self._validate_input(a)
        b_dec = self._validate_input(b)
        if b_dec == 0:
            raise ZeroDivisionError("Sıfıra mod alma hatası")
        result = a_dec % b_dec
        self._add_to_history(f"{a} % {b}", result)
        return result

    def percentage(self, value: Union[int, float, str, Decimal], percent: Union[int, float, str, Decimal]) -> Decimal:
        """Yüzde hesaplama."""
        value_dec = self._validate_input(value)
        percent_dec = self._validate_input(percent)
        result = (value_dec * percent_dec) / Decimal('100')
        self._add_to_history(f"{percent}% of {value}", result)
        return result

    # Trigonometrik fonksiyonlar
    def sin(self, angle: Union[int, float, str, Decimal]) -> Decimal:
        """Sinüs hesaplama (radyan cinsinden)."""
        angle_dec = self._validate_input(angle)
        result = Decimal(math.sin(float(angle_dec)))
        self._add_to_history(f"sin({angle})", result)
        return result

    def cos(self, angle: Union[int, float, str, Decimal]) -> Decimal:
        """Kosinüs hesaplama (radyan cinsinden)."""
        angle_dec = self._validate_input(angle)
        result = Decimal(math.cos(float(angle_dec)))
        self._add_to_history(f"cos({angle})", result)
        return result

    def tan(self, angle: Union[int, float, str, Decimal]) -> Decimal:
        """Tanjant hesaplama (radyan cinsinden)."""
        angle_dec = self._validate_input(angle)
        result = Decimal(math.tan(float(angle_dec)))
        self._add_to_history(f"tan({angle})", result)
        return result

    def asin(self, value: Union[int, float, str, Decimal]) -> Decimal:
        """Arcsinüs hesaplama."""
        value_dec = self._validate_input(value)
        if value_dec < -1 or value_dec > 1:
            raise ValueError("Arcsinüs için değer aralığı -1 ile 1 arasında olmalıdır")
        result = Decimal(math.asin(float(value_dec)))
        self._add_to_history(f"asin({value})", result)
        return result

    def acos(self, value: Union[int, float, str, Decimal]) -> Decimal:
        """Arkkosinüs hesaplama."""
        value_dec = self._validate_input(value)
        if value_dec < -1 or value_dec > 1:
            raise ValueError("Arkkosinüs için değer aralığı -1 ile 1 arasında olmalıdır")
        result = Decimal(math.acos(float(value_dec)))
        self._add_to_history(f"acos({value})", result)
        return result

    def atan(self, value: Union[int, float, str, Decimal]) -> Decimal:
        """Arktanjant hesaplama."""
        value_dec = self._validate_input(value)
        result = Decimal(math.atan(float(value_dec)))
        self._add_to_history(f"atan({value})", result)
        return result

    # Logaritmik fonksiyonlar
    def log(self, value: Union[int, float, str, Decimal], base: Union[int, float, str, Decimal] = 10) -> Decimal:
        """Logaritma hesaplama (varsayılan base 10)."""
        value_dec = self._validate_input(value)
        base_dec = self._validate_input(base)

        if value_dec <= 0 or base_dec <= 0 or base_dec == 1:
            raise ValueError("Logaritma için geçersiz değerler")

        result = Decimal(math.log(float(value_dec), float(base_dec)))
        self._add_to_history(f"log({value}, {base})", result)
        return result

    def ln(self, value: Union[int, float, str, Decimal]) -> Decimal:
        """Doğal logaritma (ln) hesaplama."""
        value_dec = self._validate_input(value)
        if value_dec <= 0:
            raise ValueError("Doğal logaritma için değer pozitif olmalıdır")
        result = Decimal(math.log(float(value_dec)))
        self._add_to_history(f"ln({value})", result)
        return result

    # Bellek fonksiyonları
    def memory_add(self, value: Union[int, float, str, Decimal]) -> None:
        """Belleğe ekleme (M+)."""
        value_dec = self._validate_input(value)
        self.memory += value_dec
        self._add_to_history(f"M+ {value}", self.memory)

    def memory_subtract(self, value: Union[int, float, str, Decimal]) -> None:
        """Bellekten çıkarma (M-)."""
        value_dec = self._validate_input(value)
        self.memory -= value_dec
        self._add_to_history(f"M- {value}", self.memory)

    def memory_recall(self) -> Decimal:
        """Belleği geri çağırma (MR)."""
        self._add_to_history("MR", self.memory)
        return self.memory

    def memory_clear(self) -> None:
        """Belleği temizleme (MC)."""
        self.memory = Decimal('0')
        self._add_to_history("MC", self.memory)

    def get_history(self) -> List[Tuple[str, Decimal]]:
        """Geçmişi döndürür."""
        return self.history.copy()

    def clear_history(self) -> None:
        """Geçmişi temizler."""
        self.history.clear()
        self._add_to_history("Clear History", Decimal('0'))

# Örnek kullanım
if __name__ == "__main__":
    calc = AdvancedCalculator()

    # Temel işlemler
    print("2 + 3 =", calc.add(2, 3))
    print("5 - 2 =", calc.subtract(5, 2))
    print("4 * 6 =", calc.multiply(4, 6))
    print("10 / 2 =", calc.divide(10, 2))
    print("2 ^ 8 =", calc.power(2, 8))
    print("√25 =", calc.sqrt(25))
    print("5! =", calc.factorial(5))
    print("10 % 3 =", calc.mod(10, 3))
    print("20% of 150 =", calc.percentage(150, 20))

    # Trigonometrik fonksiyonlar
    print("sin(π/2) =", calc.sin(math.pi/2))
    print("cos(0) =", calc.cos(0))
    print("tan(π/4) =", calc.tan(math.pi/4))

    # Logaritmik fonksiyonlar
    print("log10(100) =", calc.log(100))
    print("ln(e) =", calc.ln(math.e))

    # Bellek işlemleri
    calc.memory_add(10)
    calc.memory_add(20)
    print("Bellek değeri:", calc.memory_recall())
    calc.memory_subtract(5)
    print("Bellek değeri:", calc.memory_recall())
    calc.memory_clear()
    print("Bellek değeri:", calc.memory_recall())

    # Geçmişi göster
    print("\nİşlem geçmişi:")
    for op, result in calc.get_history():
        print(f"{op} = {result}")
```

Düzenlemeler ve iyileştirmeler:

1. **Dokümantasyon iyileştirmeleri**:
   - Sınıf ve metod dokümantasyonlarını daha anlaşılır hale getirdim
   - Desteklenen tüm işlemleri açıkça listeledim

2. **Kod yapısı iyileştirmeleri**:
   - Tüm metodları daha tutarlı bir şekilde düzenledim
   - Giriş doğrulama için özel bir metod ekledim (_validate_input)
   - Geçmiş kaydı için özel bir metod ekledim (_add_to_history)

3. **Hata yönetimi**:
   - Sıfıra bölme, negatif sayıların karekökü gibi durumlar için özel hata kontrolleri ekledim
   - Decimal dönüşümlerinde oluşabilecek hataları yakalamak için try-except bloğu ekledim

4. **Fonksiyonellik iyileştirmeleri**:
   - Bellek fonksiyonlarını tam olarak uyguladım
   - Trigonometrik fonksiyonları radyan cinsinden hesaplayacak şekilde düzenledim
   - Logaritma fonksiyonuna temel parametresi ekledim

5. **Örnek kullanım**:
   - Ana bloğa kullanım örneği ekledim
   - Tüm desteklenen işlemleri gösteren bir test senaryosu hazırladım

6. **Kod temizliği**:
   - Gereksiz boşlukları ve satırları temizledim
   - Tüm metodları tutarlı bir şekilde düzenledim
   - Tür ipuçlarını (type hints) düzenledim

Bu düzenlenmiş versiyon daha okunabilir, daha güvenilir ve daha kullanışlı hale gelmiştir.