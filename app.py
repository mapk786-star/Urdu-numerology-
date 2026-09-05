from flask import Flask, request, jsonify, send_file
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors

app = Flask(__name__)

# ---------- ABJAD NUMBERS (URDU) ----------
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
    1: "1, 3, 5, 9", 2: "2, 4, 6, 8", 3: "1, 3, 5, 9",
    4: "2, 4, 6, 8", 5: "1, 3, 5, 9", 6: "2, 4, 6, 8",
    7: "1, 3, 5, 9", 8: "2, 4, 6, 8", 9: "1, 3, 5, 9"
}

# ---------- ENGLISH NUMEROLOGY (PYTHAGOREAN) ----------
english_values = {
    'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8,'i':9,
    'j':1,'k':2,'l':3,'m':4,'n':5,'o':6,'p':7,'q':8,'r':9,
    's':1,'t':2,'u':3,'v':4,'w':5,'x':6,'y':7,'z':8
}

english_meanings = {
    1: "Leader — Confident, ambitious, independent",
    2: "Peacemaker — Diplomatic, sensitive, cooperative",
    3: "Creative — Expressive, joyful, artistic",
    4: "Builder — Practical, reliable, disciplined",
    5: "Adventurer — Curious, energetic, versatile",
    6: "Nurturer — Responsible, caring, family-oriented",
    7: "Thinker — Analytical, spiritual, introspective",
    8: "Achiever — Powerful, successful, influential",
    9: "Humanitarian — Generous, idealistic, compassionate"
}

english_lucky = {
    1: {"day": "Sunday, Friday", "color": "Red, Orange", "gem": "Ruby", "numbers": "1,10,19,28", "business": "Leadership roles"},
    2: {"day": "Monday, Thursday", "color": "White, Silver", "gem": "Pearl", "numbers": "2,11,20,29", "business": "Partnerships"},
    3: {"day": "Thursday, Friday", "color": "Yellow, Gold", "gem": "Topaz", "numbers": "3,12,21,30", "business": "Creative/Arts"},
    4: {"day": "Wednesday, Saturday", "color": "Green, Blue", "gem": "Emerald", "numbers": "4,13,22,31", "business": "Property/Construction"},
    5: {"day": "Monday, Thursday", "color": "Blue, Light", "gem": "Turquoise", "numbers": "5,14,23,32", "business": "Travel/Trading"},
    6: {"day": "Friday, Sunday", "color": "Pink, Purple", "gem": "Sapphire", "numbers": "6,15,24,33", "business": "Beauty/Home"},
    7: {"day": "Monday, Wednesday", "color": "Violet, Black", "gem": "Diamond", "numbers": "7,16,25,34", "business": "Technology"},
    8: {"day": "Saturday, Sunday", "color": "Dark Blue, Red", "gem": "Garnet", "numbers": "8,17,26,35", "business": "Banking/Finance"},
    9: {"day": "Thursday, Friday", "color": "Gold, Orange", "gem": "Topaz", "numbers": "9,18,27,36", "business": "Charity/Services"}
}

english_compatibility = {
    1: "1, 3, 5, 9", 2: "2, 4, 6, 8", 3: "1, 3, 5, 9",
    4: "2, 4, 6, 8", 5: "1, 3, 5, 9", 6: "2, 4, 6, 8",
    7: "1, 3, 5, 9", 8: "2, 4, 6, 8", 9: "1, 3, 5, 9"
}

# ---------- CALCULATION FUNCTION ----------
def calculate(name, system='urdu'):
    total = 0
    details = []
    
    if system == 'urdu':
        values = abjad
        for char in name:
            val = values.get(char, 0)
            if val > 0:
                details.append(f"{char} = {val}")
                total += val
    else:  # english
        values = english_values
        for char in name.lower():
            val = values.get(char, 0)
            if val > 0:
                details.append(f"{char} = {val}")
                total += val
    
    # Reduce to single digit (keep master numbers)
    while total > 9 and total not in [11, 22, 33]:
        total = sum(int(d) for d in str(total))
    
    # Get meaning
    if system == 'english':
        meaning = english_meanings.get(total, "Special number — You're unique!")
    else:
        meaning = meanings.get(total, "خاص عدد — آپ منفرد ہیں!")
    
    return details, total, meaning

# ---------- PDF GENERATION ----------
def generate_pdf(name, total, meaning, system='urdu'):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Title', fontName='Helvetica', fontSize=24, alignment=TA_CENTER, textColor=colors.HexColor('#7c3aed')))
    styles.add(ParagraphStyle(name='Body', fontName='Helvetica', fontSize=14, alignment=TA_RIGHT if system=='urdu' else TA_CENTER))
    styles.add(ParagraphStyle(name='Center', fontName='Helvetica', fontSize=14, alignment=TA_CENTER))
    
    if system == 'urdu':
        lucky = lucky_data.get(total, {})
        compat = compatibility.get(total, 'N/A')
        story = []
        story.append(Paragraph("🌟 عدد نام کی مکمل رپورٹ 🌟", styles['Title']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"📛 نام: {name}", styles['Body']))
        story.append(Paragraph(f"🔢 عدد: {total}", styles['Body']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("📊 شخصیت کی تحلیل:", styles['Body']))
        story.append(Paragraph(f"🧠 {meaning}", styles['Body']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("📅 خوش قسمت دن: " + lucky.get('day', 'N/A'), styles['Body']))
        story.append(Paragraph("🎨 خوش قسمت رنگ: " + lucky.get('color', 'N/A'), styles['Body']))
        story.append(Paragraph("💎 خوش قسمت پتھر: " + lucky.get('gem', 'N/A'), styles['Body']))
        story.append(Paragraph("🔮 خوش قسمت نمبرز: " + lucky.get('numbers', 'N/A'), styles['Body']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"👫 پارٹنر کی مناسبت: {compat}", styles['Body']))
        story.append(Paragraph(f"💼 کاروبار کے لیے تجاویز: {lucky.get('business', 'N/A')}", styles['Body']))
        story.append(Spacer(1, 30))
        story.append(Paragraph("🌟━━━━━━━━━━━━━━━━━━━━━━━━━━🌟", styles['Center']))
        story.append(Paragraph("شکریہ! 🌹", styles['Center']))
    else:
        lucky = english_lucky.get(total, {})
        compat = english_compatibility.get(total, 'N/A')
        story = []
        story.append(Paragraph("🌟 Complete Numerology Report 🌟", styles['Title']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"📛 Name: {name}", styles['Center']))
        story.append(Paragraph(f"🔢 Number: {total}", styles['Center']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("📊 Personality Analysis:", styles['Center']))
        story.append(Paragraph(f"🧠 {meaning}", styles['Center']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("📅 Lucky Days: " + lucky.get('day', 'N/A'), styles['Center']))
        story.append(Paragraph("🎨 Lucky Colors: " + lucky.get('color', 'N/A'), styles['Center']))
        story.append(Paragraph("💎 Lucky Gemstone: " + lucky.get('gem', 'N/A'), styles['Center']))
        story.append(Paragraph("🔮 Lucky Numbers: " + lucky.get('numbers', 'N/A'), styles['Center']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"👫 Compatibility: {compat}", styles['Center']))
        story.append(Paragraph(f"💼 Business Advice: {lucky.get('business', 'N/A')}", styles['Center']))
        story.append(Spacer(1, 30))
        story.append(Paragraph("🌟━━━━━━━━━━━━━━━━━━━━━━━━━━🌟", styles['Center']))
        story.append(Paragraph("Thank you! 🌹", styles['Center']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------- ROUTES ----------
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>عدد نام - Numerology</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a0a;color:white;font-family:sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}
        .card{background:#1a1a2e;border-radius:30px;padding:40px;max-width:500px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,0.8)}
        h1{color:#a78bfa;text-align:center;font-size:2.5rem}
        h1 small{font-size:1rem;display:block;color:#94a3b8}
        .subtitle{text-align:center;color:#94a3b8;margin:10px 0 20px}
        .lang-buttons{display:flex;gap:10px;margin:10px 0;justify-content:center}
        .lang-btn{padding:8px 20px;border:none;border-radius:10px;cursor:pointer;font-size:1rem;color:white}
        .lang-btn.active{background:#7c3aed}
        .lang-btn.inactive{background:#333}
        input{width:100%;padding:15px;font-size:1.5rem;border:2px solid #333;border-radius:15px;margin:10px 0 20px;text-align:center;background:#0a0a0a;color:white}
        input:focus{outline:none;border-color:#a78bfa}
        .calc-btn{width:100%;padding:15px;font-size:1.5rem;background:#7c3aed;color:white;border:none;border-radius:15px;cursor:pointer}
        .calc-btn:hover{background:#6d28d9}
        .result{background:#0a0a0a;border-radius:15px;padding:20px;margin-top:20px;display:none;border:1px solid #333}
        .result.show{display:block}
        .total{font-size:3rem;color:#a78bfa;text-align:center;font-weight:bold}
        .details{line-height:2;padding:10px 0;color:#e2e8f0;text-align:center}
        .meaning{background:rgba(167,139,250,0.1);padding:15px;border-radius:10px;margin-top:10px;color:#e2e8f0;text-align:center}
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
        .urdu-text{font-family:'Noto Nastaliq Urdu',sans-serif}
    </style>
    </head>
    <body>
    <div class="card">
        <h1>🔢 عدد نام <small>Name Numerology</small></h1>
        
        <div class="lang-buttons">
            <button onclick="setLanguage('urdu')" id="urduBtn" class="lang-btn active">🇵🇰 اردو</button>
            <button onclick="setLanguage('english')" id="engBtn" class="lang-btn inactive">🇬🇧 English</button>
        </div>
        
        <p class="subtitle" id="subtitle">اپنا نام لکھیں اور اپنا عدد معلوم کریں</p>
        <input id="name" placeholder="مثال: علی" />
        <button onclick="calculate()" class="calc-btn" id="calcBtn">🔮 شمار کریں</button>
        
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
    let currentName = '', currentTotal = 0, currentMeaning = '', currentLang = 'urdu';
    
    function setLanguage(lang) {
        currentLang = lang;
        document.getElementById('urduBtn').className = 'lang-btn ' + (lang === 'urdu' ? 'active' : 'inactive');
        document.getElementById('engBtn').className = 'lang-btn ' + (lang === 'english' ? 'active' : 'inactive');
        document.getElementById('name').placeholder = lang === 'urdu' ? 'مثال: علی' : 'Example: Ali';
        document.getElementById('subtitle').textContent = lang === 'urdu' ? 'اپنا نام لکھیں اور اپنا عدد معلوم کریں' : 'Enter your name to find your number';
        document.getElementById('calcBtn').textContent = lang === 'urdu' ? '🔮 شمار کریں' : '🔮 Calculate';
        document.getElementById('result').className = 'result';
        document.getElementById('result').innerHTML = '';
        document.getElementById('reportButtons').className = 'hidden';
    }
    
    async function calculate() {
        const name = document.getElementById('name').value.trim();
        if(!name) {
            alert(currentLang === 'urdu' ? 'براہ کرم نام لکھیں' : 'Please enter a name');
            return;
        }
        currentName = name;
        const resultDiv = document.getElementById('result');
        resultDiv.className = 'result show';
        resultDiv.innerHTML = '⏳ ' + (currentLang === 'urdu' ? 'حساب لگ رہا ہے...' : 'Calculating...');
        
        try {
            const endpoint = currentLang === 'urdu' ? '/api/' : '/api/english/';
            const res = await fetch(endpoint + encodeURIComponent(name));
            const data = await res.json();
            currentTotal = data.total;
            currentMeaning = data.meaning;
            
            let detailsHtml = data.details.join('<br>');
            resultDiv.innerHTML = `
                <div class="total">${data.total}</div>
                <div class="details">${detailsHtml}</div>
                <div class="meaning">🧠 ${data.meaning}</div>
            `;
            document.getElementById('reportButtons').className = '';
        } catch(e) {
            resultDiv.innerHTML = '❌ Error: ' + e.message;
        }
    }
    
    function downloadReport() {
        if(!currentName) {
            alert(currentLang === 'urdu' ? 'براہ کرم پہلے نام چیک کریں' : 'Please check a name first');
            return;
        }
        window.open('/download/' + encodeURIComponent(currentName) + '/' + currentTotal + '/' + encodeURIComponent(currentMeaning) + '?lang=' + currentLang);
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
        alert('✅ ' + (currentLang === 'urdu' ? 'لنک کاپی ہو گیا!' : 'Link copied!'));
    }
    </script>
    </body>
    </html>
    '''

@app.route('/api/<name>')
def api(name):
    details, total, meaning = calculate(name, 'urdu')
    return jsonify({'details': details, 'total': total, 'meaning': meaning})

@app.route('/api/english/<name>')
def api_english(name):
    details, total, meaning = calculate(name, 'english')
    return jsonify({'details': details, 'total': total, 'meaning': meaning})

@app.route('/download/<name>/<int:total>/<meaning>')
def download_report(name, total, meaning):
    lang = request.args.get('lang', 'urdu')
    pdf_buffer = generate_pdf(name, total, meaning, lang)
    return send_file(pdf_buffer, as_attachment=True, download_name=f"{name}_report.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
