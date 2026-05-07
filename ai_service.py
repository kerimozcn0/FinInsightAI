import requests
import base64
import json
import re

N8N_WEBHOOK_URL = "" #BURAYA APİ KEY GİRİLECEK.

def process_financial_document(filename, content):
    try:
        payload = {"file_name": filename}
        
        
        if filename.endswith(('.xls', '.xlsx')):
            try:
                import pandas as pd
                import io
                df = pd.read_excel(io.BytesIO(content))
                payload["file_type"] = "excel_text"
                payload["text_data"] = df.to_json(orient="records", force_ascii=False)
            except Exception as e:
                return {"status": "error", "message": f"Excel okuma hatası: {str(e)}", "data": []}
        else:
            payload["file_type"] = "document"
            payload["file_data"] = base64.b64encode(content).decode('utf-8')

        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=300)
        
        if response.status_code != 200:
            return {"status": "error", "message": f"n8n Hatası! (Kod: {response.status_code})", "data": []}

        n8n_raw = response.text 
        match = re.search(r'\[[\s\S]*\]|\{[\s\S]*\}', n8n_raw)
        companies_data = []
        
        if match:
            json_str = match.group(0).replace('```json', '').replace('```', '')
            try:
                parsed_data = json.loads(json_str)
                if isinstance(parsed_data, list):
                    companies_data = parsed_data
                elif isinstance(parsed_data, dict):
                    if "text" in parsed_data and isinstance(parsed_data["text"], str):
                        inner_match = re.search(r'\[[\s\S]*\]|\{[\s\S]*\}', parsed_data["text"])
                        if inner_match:
                            inner_parsed = json.loads(inner_match.group(0).replace('```json', '').replace('```', ''))
                            companies_data = inner_parsed if isinstance(inner_parsed, list) else [inner_parsed]
                    else:
                        companies_data = [parsed_data]
            except Exception:
                pass
        
        if not companies_data:
            companies_data = [{}]

        formatted_companies = []
        for data in companies_data:
            vkn = data.get("vergi_no", "")
            if not vkn or vkn == "Vergi No Yok":
                import random
                vkn = f"Bilinmiyor-{random.randint(1000,9999)}"

        
            bankalar_raw = data.get("bankalar_ve_detaylar", [])
            bankalar_text = ""
            if isinstance(bankalar_raw, list) and len(bankalar_raw) > 0:
                for b in bankalar_raw:
                    b_isim = b.get("isim", "Bilinmeyen Banka")
                    b_borc = b.get("borc", 0)
                    b_limit = b.get("limit", 0)
                    bankalar_text += f"- {b_isim} | Borç: {b_borc} TL | Limit: {b_limit} TL\n"
            else:
                bankalar_text = "Detaylı banka kırılımı bulunamadı."

            formatted_companies.append({
                "firma_unvani": data.get("firma_unvani", "İsimsiz Firma"),
                "vergi_no": vkn,
                "toplam_borc": f"{data.get('toplam_borc_tl', 0)} TL",
                "toplam_limit": f"{data.get('toplam_limit_tl', 0)} TL",
                "risk_skoru": data.get("risk_durumu", "Belirsiz"),
                "ai_uzman_gorusu": data.get("uzman_gorusu", "Uzman görüşü bulunamadı."),
                "banka_limit": bankalar_text 
            })

        return {"status": "success", "data": formatted_companies}
            
    except Exception as e:
        return {"status": "error", "message": f"Sistem hatası: {str(e)}", "data": []}
