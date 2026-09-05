from flask import Flask, request, jsonify, send_file
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

app = Flask(__name__)

# ---------- ABJAD NUMBERS ----------
abjad = {
'ا':1,'ب':2,'ج':3,'د':4,'ہ':5,'و':6,'ز':7,'ح':8,'ط':9,'ی':10,
'ك':20,'ل':30,'م':40,'ن':50,'س':60,'ع':70,'ف':80,'ص':90,'ق':100,
'ر':200,'ش':300,'ت':400,'ث':500,'خ':600,'ذ':700,'ض':800,'ظ':900,'غ':1000
}

meanings = {
    1: "رہنما — خود اعتماد، باصلاحیت، آزاد مزاج",
    2: "دوست — نرم دل، محبت کرنے والا، تعاون پسند",
    3: "تخلیقی — فنکار، مزاحیہ، خوش مزاج",
    4: "محنتی — مضبوط، قابل اعتماد، منظم",
    5: "آزاد — سفر پسند، تجسس خور، تیز",
    6: "محبت کرنے والا — ذمہ دار، شفیق، خاندانی",
    7: "فلسفی — گہرا، خاموش، علم دوست",
    8: "کامیاب — طاقتور، امیر، بااثر",
    9: "انسان دوست — فیاض، مثالی، بلند نظر"
}

lucky_data = {
    1: {"day": "جمعہ, اتوار", "color": "سرخ, نارنجی", "gem": "روبی", "numbers": "1, 10, 19, 28", "business": "لیڈرشپ والے کاروبار"},
    2: {"day": "پیر, جمعرات", "color": "سفید, چاندی", "gem": "موتی", "numbers": "2, 11, 20, 29", "business": "پارٹنرشپ"},
    3: {"day": "جمعرات, جمعہ", "color": "پیلا, سنہری", "gem": "پکھراج", "numbers": "3, 12, 21, 30", "business": "تخلیقی/آرٹ"},
    4: {"day": "بدھ, ہفتہ", "color": "سبز, نیلا", "gem": "زمرد", "numbers": "4, 13, 22, 31", "business": "پراپرٹی/تعمیرات"},
    5: {"day": "پیر, جمعرات", "color": "نیلا, ہلکا", "gem": "فیروزہ", "numbers": "5, 14, 23, 32", "business": "سفری/ٹریڈنگ"},
    6: {"day": "جمعہ, اتوار", "color": "گلابی, جامنی", "gem": "نیلم", "numbers": "6, 15, 24, 33", "business": "خوبصورتی/ہوم"},
    7: {"day": "پیر, بدھ", "color": "بنفشی, سیاہ", "gem": "ہیرا", "numbers": "7, 16, 25, 34", "business": "ٹیکنالوجی"},
    8: {"day": "ہفتہ, اتوار", "color": "گہرا نیلا, سرخ", "gem": "گارنیٹ", "numbers": "8, 17, 26, 35", "business": "بینکنگ/مالیات"},
    9: {"day": "جمعرات, جمعہ", "color": "سنہری, نارنجی", "gem": "پکھراج", "numbers": "9, 18, 27, 36", "business": "خیراتی/خدمات"}
}

compatibility = {
    1: "1, 3, 5, 9",
    2: "2, 4, 6, 8",
    3: "1, 3, 5, 9",
    4: "2, 4, 6, 8",
    5: "1, 3, 5, 9",
    6: "2, 4, 6, 8",
    7: "1, 3, 5, 9",
    8: "2, 4, 6, 8",
    9: "1, 3, 5, 9"
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
    return details, total, meanings.get(total, "خاص عدد — آپ منفرد ہیں!")

def generate_pdf(name, total, meaning):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(name='UrduTitle', fontName='Helvetica', fontSize=24, alignment=TA_CENTER, textColor=colors.HexColor('#7c3aed')))
    styles.add(ParagraphStyle(name='UrduBody', fontName='Helvetica', fontSize=14, alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='UrduCenter', fontName='Helvetica', fontSize=14, alignment=TA_CENTER))
    
    lucky = lucky_data.get(total, {})
    
    story = []
    
    story.append(Paragraph("🌟 عدد نام کی مکمل رپورٹ 🌟", styles['UrduTitle']))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"📛 نام: {name}", styles['UrduBody']))
    story.append(Paragraph(f"🔢 عدد: {total}", styles['UrduBody']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("📊 شخصیت کی تحلیل:", styles['UrduBody']))
    story.append(Paragraph(f"🧠 {meaning}", styles['UrduBody']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("📅 خوش قسمت دن: " + lucky.get('day', 'N/A'), styles['UrduBody']))
    story.append(Paragraph("🎨 خوش قسمت رنگ: " + lucky.get('color', 'N/A'), styles['UrduBody']))
    story.append(Paragraph("💎 خوش قسمت پتھر: " + lucky.get('gem', 'N/A'), styles['UrduBody']))
    story.append(Paragraph("🔮 خوش قسمت نمبرز: " + lucky.get('numbers', 'N/A'), styles['UrduBody']))
    story.append(Spacer(1, 20))
    compat = compatibility.get(total, "N/A")
    story.append(Paragraph(f"👫 پارٹنر کی مناسبت: {compat}", styles['UrduBody']))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"💼 کاروبار کے لیے تجاویز: {lucky.get('business', 'N/A')}", styles['UrduBody']))
    story.append(Spacer(1, 30))
    story.append(Paragraph("🌟━━━━━━━━━━━━━━━━━━━━━━━━━━🌟", styles['UrduCenter']))
    story.append(Paragraph("شکریہ! 🌹", styles['UrduCenter']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head><meta charset="UTF-8"><title>عدد نام</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a0a;color:white;font-family:'Noto Nastaliq Urdu',sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}
        .card{background:#1a1a2e;border-radius:30px;padding:40px;max-width:500px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,0.8)}
        h1{color:#a78bfa;text-align:center;font-size:2.5rem}
        h1 small{font-size:1rem;display:block;color:#94a3b8}
        .subtitle{text-align:center;color:#94a3b8;margin:10px 0 20px}
        input{width:100%;padding:15px;font-size:1.5rem;border:2px solid #333;border-radius:15px;margin:10px 0 20px;text-align:right;background:#0a0a0a;color:white}
        input:focus{outline:none;border-color:#a78bfa}
        button{width:100%;padding:15px;font-size:1.5rem;background:#7c3aed;color:white;border:none;border-radius:15px;cursor:pointer}
        button:hover{background:#6d28d9}
        .result{background:#0a0a0a;border-radius:15px;padding:20px;margin-top:20px;display:none;border:1px solid #333}
        .result.show{display:block}
        .total{font-size:3rem;color:#a78bfa;text-align:center;font-weight:bold}
        .details{line-height:2;padding:10px 0;color:#e2e8f0}
        .meaning{background:rgba(167,139,250,0.1);padding:15px;border-radius:10px;margin-top:10px;color:#e2e8f0}
        .whatsapp-btn{background:#25D366;color:white;padding:12px;border-radius:10px;text-decoration:none;display:block;text-align:center;margin-top:15px;font-size:1.2rem}
        .whatsapp-btn:hover{background:#128C7E}
        .download-btn{background:#f59e0b;color:white;padding:12px;border-radius:10px;text-decoration:none;display:block;text-align:center;margin-top:10px;font-size:1.2rem;cursor:pointer;border:none;width:100%}
        .download-btn:hover{background:#d97706}
        .share-buttons{display:flex;gap:10px;margin-top:15px;flex-wrap:wrap}
        .share-btn{flex:1;padding:10px;border:none;border-radius:10px;color:white;cursor:pointer;font-size:0.9rem;text-align:center;min-width:60px}
        .share-whatsapp{background:#25D366}
        .share-facebook{background:#1877F2}
        .share-twitter{background:#000}
        .share-copy{background:#7c3aed}
        .footer{text-align:center;margin-top:20px;color:#64748b}
        .payment-info{background:rgba(245,158,11,0.1);border:1px solid #f59e0b;border-radius:10px;padding:15px;margin-top:15px}
        .payment-info h3{color:#f59e0b;text-align:center}
        .payment-info p{color:#94a3b8;text-align:center;margin:5px 0}
        .hidden{display:none}
    </style>
    </head>
    <body>
    <div class="card">
        <h1>🔢 عدد نام <small>Name Numerology</small></h1>
        <p class="subtitle">اپنا نام لکھیں اور اپنا عدد معلوم کریں</p>
        <input id="name" placeholder="مثال: علی" />
        <button onclick="calculate()">🔮 شمار کریں</button>
        <div class="result" id="result"></div>
        <div id="reportButtons" class="hidden">
            <button onclick="downloadReport()" class="download-btn">📄 مکمل رپورٹ ڈاؤن لوڈ کریں (PKR 500)</button>
            <div class="payment-info">
                <h3>💰 ادائیگی کی معلومات</h3>
                <p>📱 JazzCash: 0312-0497193</p>
                <p>📱 Easypaisa: 0312-0497193</p>
                <p style="font-size:0.8rem;color:#64748b">⚠️ رپورٹ ڈاؤن لوڈ کرنے کے لیے پہلے PKR 500 بھیجیں</p>
            </div>
        </div>
        <a href="https://wa.me/923120497193?text=مجھے%20مکمل%20رپورٹ%20چاہیے" class="whatsapp-btn">
            📱 مکمل رپورٹ (PKR 500) - WhatsApp پر رابطہ کریں
        </a>
        <div class="share-buttons">
            <button onclick="shareWhatsApp()" class="share-btn share-whatsapp">📱 شیئر</button>
            <button onclick="shareFacebook()" class="share-btn share-facebook">📘</button>
            <button onclick="shareTwitter()" class="share-btn share-twitter">🐦</button>
            <button onclick="copyLink()" class="share-btn share-copy">📋 لنک</button>
        </div>
        <div class="footer">🔮 اپنے دوستوں کے نام بھی چیک کروائیں</div>
    </div>
    <script>
    let currentName = '';
    let currentTotal = 0;
    let currentMeaning = '';

    async function calculate() {
        const name = document.getElementById('name').value.trim();
        if(!name) { alert('براہ کرم نام لکھیں'); return; }
        currentName = name;
        const resultDiv = document.getElementById('result');
        resultDiv.className = 'result show';
        resultDiv.innerHTML = '⏳ حساب لگ رہا ہے...';
        try {
            const res = await fetch('/api/' + encodeURIComponent(name));
            const data = await res.json();
            currentTotal = data.total;
            currentMeaning = data.meaning;
            resultDiv.innerHTML = `
                <div class="total">${data.total}</div>
                <div class="details">${data.details.join('<br>')}</div>
                <div class="meaning">🧠 ${data.meaning}</div>
            `;
            document.getElementById('reportButtons').className = '';
        } catch(e) {
            resultDiv.innerHTML = '❌ Error: ' + e.message;
        }
    }

    function downloadReport() {
        if(!currentName) {
            alert('براہ کرم پہلے نام چیک کریں');
            return;
        }
        window.open('/download/' + encodeURIComponent(currentName) + '/' + currentTotal + '/' + encodeURIComponent(currentMeaning));
    }

    document.getElementById('name').addEventListener('keypress', function(e) {
        if(e.key === 'Enter') calculate();
    });

    function shareWhatsApp() {
        window.open('https://wa.me/923120497193?text=' + encodeURIComponent('🔮 اپنا عدد نام چیک کریں! ' + window.location.href));
    }
    function shareFacebook() {
        window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(window.location.href));
    }
    function shareTwitter() {
        window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent('🔮 اپنا عدد نام چیک کریں!') + '&url=' + encodeURIComponent(window.location.href));
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

@app.route('/download/<name>/<int:total>/<meaning>')
def download_report(name, total, meaning):
    pdf_buffer = generate_pdf(name, total, meaning)
    return send_file(pdf_buffer, as_attachment=True, download_name=f"{name}_report.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
