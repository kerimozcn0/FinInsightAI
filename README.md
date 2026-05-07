# PROSICHT - AI Destekli Finansal Rapor Analizörü

Bu proje, BSMT Hackathon kapsamında 24 saatlik kısıtlı bir süre içinde geliştirilmiş bir Minimum Viable Product (MVP) çalışmasıdır. Temel amacı; danışmanlık ve finans firmalarının saatlerini alan manuel veri girişi süreçlerini, OCR ve LLM (Büyük Dil Modelleri) kullanarak otomatize etmektir.
NOT: 24 saat içerisinde n8n ve ai pipeline kısmı tamamen 0 dan öğrenildi. Artık yapımcı kurduğu sistem üzerine yapay zeka bağlamayı ve yapay zekaya senkronize şekilde bilgi ayıklatıp geri sisteme yollatıp çıktı oluşturmayı öğrendi.++
## Proje Özeti
Prosicht, sisteme yüklenen karmaşık finansal belgeleri (Findeks Raporları, Mizan Tabloları vb.) analiz eder, içindeki borç/limit/risk verilerini ayrıştırır ve yapılandırılmış JSON formatında backend'e iletir. Sistem aynı zamanda elde edilen ham verileri yorumlayarak profesyonel bir finansal durum özeti (Uzman Görüşü) üretir.

## 🛠️ Teknik Mimari & Teknoloji Yığını

* **Backend:** Python, FastAPI, Uvicorn
* **Veritabanı:** SQLite, SQLAlchemy (ORM)
* **Frontend:** HTML5, Tailwind CSS, Chart.js, Jinja2 Template Engine
* **AI Pipeline:** n8n (Workflow Automation), Google Gemini (LLM & OCR)

## Proje Yapısı

* `main.py`: FastAPI sunucu yapılandırması, routing ve CRUD işlemleri.
* `ai_service.py`: N8n webhook'ları ile haberleşen, yüklenen belgeleri base64 veya text formatında işleyip JSON olarak parse eden servis katmanı.
* `models.py`: SQLAlchemy veritabanı tablolarının tanımlandığı şema dosyası.
* `database.py`: Veritabanı bağlantı yönetimi.
* `templates/`: Kullanıcı ve Admin arayüzlerini barındıran Jinja2 destekli HTML dosyaları (`index.html`, `admin.html`, `company_detail.html`).
