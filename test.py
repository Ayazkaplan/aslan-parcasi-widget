"""
test.py - VX tarafından oluşturuldu
"""
from flask import Flask, render_template_string, request, jsonify
import datetime

app = Flask(__name__)

# Ana sayfa HTML
HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aslan Parçası Widget - VX</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
        }
        h1 {
            font-size: 3em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            color: rgba(255, 255, 255, 0.7);
            font-size: 1.1em;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }
        .card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .card p {
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.6;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .grid-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }
        .grid-item:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }
        .grid-item .number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 10px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: rgba(255, 255, 255, 0.4);
            font-size: 0.9em;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 20px;
        }
        .status {
            display: inline-block;
            background: #2ecc71;
            color: white;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.8em;
        }
        .status.offline {
            background: #e74c3c;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌌 VERTIXORION OMEGA</h1>
        <p class="subtitle">Aslan Parçası Widget - Yapay Zeka Destekli Platform</p>
        
        <div style="margin-bottom: 20px;">
            <span class="status">● Çevrimiçi</span>
            <span style="margin-left: 15px; color: rgba(255,255,255,0.5);">v2.0.1</span>
        </div>
        
        <div class="grid">
            <div class="grid-item">
                <div class="number">10+</div>
                <div>Uzman Ajan</div>
            </div>
            <div class="grid-item">
                <div class="number">∞</div>
                <div>Kod Kapasitesi</div>
            </div>
            <div class="grid-item">
                <div class="number">%99</div>
                <div>Doğruluk</div>
            </div>
            <div class="grid-item">
                <div class="number">⚡</div>
                <div>Hızlı İşlem</div>
            </div>
        </div>
        
        <div class="card">
            <h3>🚀 Yetenekler</h3>
            <p>
                • Dosyaları görüntüle, oluştur ve güncelle<br>
                • 10 uzman ajan ile güçlü analiz<br>
                • GitHub entegrasyonu<br>
                • Otomatik kod optimizasyonu<br>
                • Güvenlik taraması
            </p>
        </div>
        
        <div class="card">
            <h3>📊 Sistem Durumu</h3>
            <p>
                <strong>Repo:</strong> aslan-parcasi-widget<br>
                <strong>Dosya Sayısı:</strong> 7<br>
                <strong>Son Güncelleme:</strong> VX tarafından<br>
                <strong>API:</strong> Mistral AI
            </p>
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="#" class="btn">🚀 Başlat</a>
            <a href="#" class="btn" style="margin-left: 10px; background: rgba(255,255,255,0.1);">📖 Doküman</a>
        </div>
        
        <div class="footer">
            &copy; 2026 VX - Aslan Parçası Widget | Tüm hakları saklıdır.
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'online',
        'version': '2.0.1',
        'timestamp': datetime.datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
