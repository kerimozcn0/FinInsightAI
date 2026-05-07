from fastapi import FastAPI, Request, File, UploadFile, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn

from database import engine, Base, get_db
import models
import ai_service

Base.metadata.create_all(bind=engine)
app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"title": "BSMT Finans AI"})

@app.post("/api/upload/")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    ai_result = ai_service.process_financial_document(file.filename, content)
    
    if ai_result.get("status") == "success":
        companies_data = ai_result.get("data", [])
        
        for data in companies_data:
            vergi_no = data.get("vergi_no", "Bilinmiyor")
            firma_unvani = data.get("firma_unvani", "İsimsiz Firma")
            
            company = db.query(models.Company).filter(models.Company.tax_number == vergi_no).first()
            if not company:
                company = models.Company(name=firma_unvani, tax_number=vergi_no)
                db.add(company)
                
            company.toplam_borc = data.get("toplam_borc", "0 TL") 
            company.toplam_limit = data.get("toplam_limit", "0 TL")
            company.risk_skoru = data.get("risk_skoru", "Belirsiz")
            company.uzman_gorusu = data.get("ai_uzman_gorusu", "Uzman görüşü bulunamadı.")
            
            company.banka_limit = data.get("banka_limit", "") 
            
        try:
            db.commit() 
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": f"Veritabanı hatası: {str(e)}", "data": []}
            
    return ai_result

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    companies = db.query(models.Company).all()
    return templates.TemplateResponse(request=request, name="admin.html", context={"companies": companies})

@app.get("/admin/company/{company_id}", response_class=HTMLResponse)
async def view_company(company_id: int, request: Request, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    return templates.TemplateResponse(request=request, name="company_detail.html", context={"company": company})

@app.post("/admin/delete_company/{company_id}")
async def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if company:
        db.delete(company)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/add_company")
async def add_company(name: str = Form(...), tax_number: str = Form(...), db: Session = Depends(get_db)):
    new_company = models.Company(name=name, tax_number=tax_number)
    db.add(new_company)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/update_company/{company_id}")
async def update_company(
    company_id: int, 
    toplam_borc: str = Form(None),
    toplam_limit: str = Form(None),
    uzman_gorusu: str = Form(None),
    bilanco: str = Form(None), 
    gelir: str = Form(None), 
    nakit_akis: str = Form(None),
    banka: str = Form(None), 
    db: Session = Depends(get_db)
):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if company:
        if toplam_borc is not None: company.toplam_borc = toplam_borc
        if toplam_limit is not None: company.toplam_limit = toplam_limit
        if uzman_gorusu is not None: company.uzman_gorusu = uzman_gorusu
        if bilanco is not None: company.bilanco_toplami = bilanco
        if gelir is not None: company.gelir_tablosu = gelir
        if nakit_akis is not None: company.nakit_akis = nakit_akis
        if banka is not None: company.banka_limit = banka 
        db.commit()
    return RedirectResponse(url=f"/admin/company/{company_id}", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8050, reload=True)
