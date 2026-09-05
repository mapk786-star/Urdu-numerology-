from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# ---------- ABJAD NUMBERS ----------
abjad = {
'ا':1,'ب':2,'ج':3,'د':4,'ہ':5,'و':6,'ز':7,'ح':8,'ط':9,'ی':10,
'ك':20,'ل':30,'م':40,'ن':50,'س':60,'ع':70,'ف':80,'ص':90,'ق':100,
'ر':200,'ش':300,'ت':400,'ث':500,'خ':600,'ذ':700,'ض':800,'ظ':900,'غ':1000
}

meanings = {
    1: "🏆 رہنما — خود اعتماد، باصلاحیت، آزاد مزاج",
    2: "🤝 دوست — نرم دل، محبت کرنے والا، تعاون پسند",
    3: "🎨 تخلیقی — فنکار، مزاحیہ، خوش مزاج",
    4: "🏗️ محنتی — مضبوط، قابل اعتماد، منظم",
    5: "🌊 آزاد — سفر پسند، تجسس خور، تیز",
    6: "❤️ محبت کرنے والا — ذمہ دار، شفیق، خاندانی",
    7: "🔍 فلسفی — گہرا، خاموش، علم دوست",
    8: "💰 کامیاب — طاقتور، امیر، بااثر",
    9: "🌟 انسان دوست — فیاض، مثالی، بلند نظر"
}

def calculate(name):
    total = 0
    details = []
    for char in name:
        val = abjad.get(char, 0)
        details.append(f"{char} = {val}")
        total += val
    while total > 9 and total not in [11, 22, 33]:
        total = sum(int(d) for d in str(total))
    return details, total, meanings.get(total, "✨ خاص عدد — آپ منفرد ہیں!")

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head><meta charset="UTF-8"><title>عدد نام</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Noto Nastaliq Urdu',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;justify-content:center;align-items:center;margin:0;padding:20px}
        .card{background:white;border-radius:30px;padding:40px;max-width:500px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,0.3);animation:fadeIn 0.5s}
        @keyframes fadeIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
        h1{color:#764ba2;text-align:center;font-size:2.5rem;margin:0}
        h1 small{font-size:1rem;display:block;color:#999;margin-top:5px}
        .subtitle{text-align:center;color:#666;margin:10px 0 20px}
        input{width:100%;padding:15px;font-size:1.5rem;border:2px solid #ddd;border-radius:15px;margin:10px 0 20px;text-align:right;transition:0.3s;font-family:inherit}
        input:focus{outline:none;border-color:#764ba2;box-shadow:0 0 10px rgba(118,75,162,0.2)}
        button{width:100%;padding:15px;font-size:1.5rem;background:#764ba2;color:white;border:none;border-radius:15px;cursor:pointer;transition:0.3s;font-family:inherit}
        button:hover{background:#667eea;transform:scale(1.02)}
        .result{background:#f8f9fa;border-radius:15px;padding:20px;margin-top:20px;font-size:1.2rem;display:none}
        .result.show{display:block}
        .total{font-size:3rem;color:#764ba2;text-align:center;font-weight:bold}
        .details{line-height:2;padding:10px 0}
        .meaning{background:#e8f5e9;padding:15px;border-radius:10px;margin-top:10px;border-right:4px solid #4CAF50}
        .whatsapp-btn{background:#25D366;color:white;padding:12px;border-radius:10px;text-decoration:none;display:block;text-align:center;margin-top:15px;font-size:1.2rem;transition:0.3s;font-family:inherit}
        .whatsapp-btn:hover{background:#128C7E;transform:scale(1.02)}
        .share-buttons{display:flex;gap:10px;margin-top:15px;flex-wrap:wrap}
        .share-btn{flex:1;padding:10px;border:none;border-radius:10px;color:white;cursor:pointer;font-size:0.9rem;transition:0.3s;font-family:inherit;text-decoration:none;text-align:center}
        .share-btn:hover{transform:scale(1.05)}
        .share-whatsapp{background:#25D366}
        .share-facebook{background:#1877F2}
        .share-twitter{background:#000}
        .share-copy{background:#764ba2}
        .footer{text-align:center;margin-top:20px;font-size:0.8rem;color:#999}
    </style>
    </head>
    <body>
    <div class="card">
        <h1>🔢 عدد نام <small>Name Numerology</small></h1>
        <p class="subtitle">اپنا نام لکھیں اور اپنا عدد معلوم کریں</p>
        <input id="name" placeholder="مثال: علی" />
        <button onclick="calculate()">🔮 شمار کریں</button>
        <div class="result" id="result">
            <div class="total" id="total"></div>
            <div class="details" id="details"></div>
            <div class="meaning" id="meaning"></div>
        </div>
        <a href="https://wa.me/923120497193?text=مجھے%20مکمل%20رپورٹ%20چاہیے" class="whatsapp-btn">
            📱 مکمل رپورٹ (PKR 500) - WhatsApp پر رابطہ کریں
        </a>
        <div class="share-buttons">
            <a href="#" onclick="shareWhatsApp()" class="share-btn share-whatsapp">📱 شیئر کریں</a>
            <a href="#" onclick="shareFacebook()" class="share-btn share-facebook">📘</a>
            <a href="#" onclick="shareTwitter()" class="share-btn share-twitter">🐦</a>
            <button onclick="copyLink()" class="share-btn share-copy">📋 لنک کاپی کریں</button>
        </div>
        <div class="footer">🔮 اپنے دوستوں کے نام بھی چیک کروائیں</div>
    </div>
    <script>
    async function calculate() {
        const name = document.getElementById('name').value.trim();
        if(!name) {
            alert('براہ کرم نام لکھیں');
            return;
        }
        const resultDiv = document.getElementById('result');
        resultDiv.className = 'result show';
        resultDiv.innerHTML = '<div class="loading">⏳ حساب لگ رہا ہے...</div>';
        try {
            const res = await fetch('/api/'+encodeURIComponent(name));
            const data = await res.json();
            resultDiv.innerHTML = `
                <div class="total">${data.total}</div>
                <div class="details">${data.details.join('<br>')}</div>
                <div class="meaning">🧠 ${data.meaning}</div>
            `;
        } catch(e) {
            resultDiv.innerHTML = '<div style="color:red;">❌ Error: '+e.message+'</div>';
        }
    }
    document.getElementById('name').addEventListener('keypress', function(e) {
        if(e.key === 'Enter') calculate();
    });
    function shareWhatsApp() {
        const url = window.location.href;
        window.open('https://wa.me/?text='+encodeURIComponent('🔮 اپنا عدد نام چیک کریں! '+url), '_blank');
    }
    function shareFacebook() {
        window.open('https://facebook.com/sharer/sharer.php?u='+encodeURIComponent(window.location.href), '_blank');
    }
    function shareTwitter() {
        window.open('https://twitter.com/intent/tweet?text='+encodeURIComponent('🔮 اپنا عدد نام چیک کریں!')+'&url='+encodeURIComponent(window.location.href), '_blank');
    }
    function copyLink() {
        navigator.clipboard.writeText(window.location.href);
        alert('✅ لنک کاپی ہو گیا!');
    }
    </script>
    </body>
    </html>
    '''

@app.route('/api/<name>')
def api(name):
    details, total, meaning = calculate(name)
    return jsonify({'details': details, 'total': total, 'meaning': meaning})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
