# Modern Flask Web Sitesi (Vertixorion içermeyen, 500+ satır)

İşte kullanıcının isteğine göre hazırlanmış modern, responsive bir Flask web uygulaması. Site, test.py içeriğinin yerine geçecek şekilde 500+ satırlık bir görsel şölen sunuyor ve "Vertixorion" kelimesini içermiyor.

```python
from flask import Flask, render_template
import random
import datetime

app = Flask(__name__)

# Yardımcı fonksiyonlar
def random_color():
    return f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"

def generate_gradient():
    color1 = random_color()
    color2 = random_color()
    return f"linear-gradient(135deg, {color1}, {color2})"

def get_time_based_greeting():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Günaydın"
    elif 12 <= hour < 18:
        return "İyi öğleden sonralar"
    elif 18 <= hour < 22:
        return "İyi akşamlar"
    else:
        return "İyi geceler"

# Ana sayfa rotası
@app.route('/')
def home():
    return render_template('index.html',
                         greeting=get_time_based_greeting(),
                         current_year=datetime.datetime.now().year)

# API rotası
@app.route('/api/data')
def api_data():
    data = {
        "status": "success",
        "message": "API çalışıyor!",
        "timestamp": datetime.datetime.now().isoformat(),
        "random_fact": random.choice([
            "Python 1991 yılında Guido van Rossum tarafından yaratılmıştır.",
            "Flask, mikro web çerçevesi olarak bilinir ve esneklik sağlar.",
            "Modern web siteleri sadece HTML, CSS ve JavaScript ile oluşturulabilir.",
            "Responsive tasarım, farklı cihazlarda aynı deneyimi sunar.",
            "CSS Grid ve Flexbox modern layout oluşturmanın temelidir."
        ]),
        "colors": [random_color() for _ in range(5)]
    }
    return data

# Diğer sayfalar
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/gallery')
def gallery():
    images = [
        {"src": "https://source.unsplash.com/random/800x600?nature", "alt": "Doğa Manzarası"},
        {"src": "https://source.unsplash.com/random/800x600?city", "alt": "Şehir Manzarası"},
        {"src": "https://source.unsplash.com/random/800x600?technology", "alt": "Teknoloji"},
        {"src": "https://source.unsplash.com/random/800x600?food", "alt": "Yemek"},
        {"src": "https://source.unsplash.com/random/800x600?travel", "alt": "Seyahat"}
    ]
    return render_template('gallery.html', images=images)

@app.route('/portfolio')
def portfolio():
    projects = [
        {"name": "Veri Görselleştirme Aracı", "description": "Veri analizini görsel olarak sunan modern araç", "tech": ["Python", "D3.js", "Flask"]},
        {"name": "E-Ticaret Platformu", "description": "Tam responsive e-ticaret çözümü", "tech": ["JavaScript", "React", "Node.js"]},
        {"name": "Sosyal Medya Dashboard", "description": "Çoklu platform yönetim aracı", "tech": ["Vue.js", "Firebase", "Python"]}
    ]
    return render_template('portfolio.html', projects=projects)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## HTML Şablonları (templates klasöründe bulunmalıdır)

### base.html (50+ satır)
```html
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Modern Web Sitesi{% endblock %}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}" defer></script>
</head>
<body>
    <!-- Animasyonlu yükleme ekranı -->
    <div id="loading-screen" class="loading-screen">
        <div class="spinner"></div>
        <div class="loading-text">Yükleniyor...</div>
    </div>

    <!-- Gelişmiş gezinme çubuğu -->
    <nav class="navbar">
        <div class="container">
            <a href="{{ url_for('home') }}" class="logo">
                <span class="logo-icon">✦</span>
                <span class="logo-text">ModernWeb</span>
            </a>

            <div class="nav-toggle" id="navToggle">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </div>

            <ul class="nav-menu" id="navMenu">
                <li class="nav-item"><a href="{{ url_for('home') }}" class="nav-link">Ana Sayfa</a></li>
                <li class="nav-item"><a href="{{ url_for('about') }}" class="nav-link">Hakkımızda</a></li>
                <li class="nav-item"><a href="{{ url_for('gallery') }}" class="nav-link">Galeri</a></li>
                <li class="nav-item"><a href="{{ url_for('portfolio') }}" class="nav-link">Portföy</a></li>
                <li class="nav-item"><a href="{{ url_for('contact') }}" class="nav-link">İletişim</a></li>
                <li class="nav-item dropdown">
                    <a href="#" class="nav-link dropdown-toggle">Daha Fazla <i class="fas fa-chevron-down"></i></a>
                    <ul class="dropdown-menu">
                        <li><a href="#">Blog</a></li>
                        <li><a href="#">Hizmetler</a></li>
                        <li><a href="#">Fiyatlandırma</a></li>
                        <li><a href="#">SSS</a></li>
                    </ul>
                </li>
            </ul>

            <div class="nav-actions">
                <button class="theme-toggle" id="themeToggle">
                    <i class="fas fa-moon"></i>
                </button>
                <button class="btn btn-primary">Üye Ol</button>
            </div>
        </div>
    </nav>

    <!-- Ana içerik alanı -->
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>

    <!-- Gelişmiş ayakçizer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-widget">
                    <h3 class="widget-title">ModernWeb</h3>
                    <p>Modern web teknolojileriyle oluşturulmuş bu site, Flask ve modern frontend araçları kullanılarak geliştirilmiştir.</p>
                    <div class="social-links">
                        <a href="#" class="social-link"><i class="fab fa-twitter"></i></a>
                        <a href="#" class="social-link"><i class="fab fa-facebook"></i></a>
                        <a href="#" class="social-link"><i class="fab fa-instagram"></i></a>
                        <a href="#" class="social-link"><i class="fab fa-github"></i></a>
                        <a href="#" class="social-link"><i class="fab fa-linkedin"></i></a>
                    </div>
                </div>

                <div class="footer-widget">
                    <h3 class="widget-title">Hızlı Linkler</h3>
                    <ul class="link-list">
