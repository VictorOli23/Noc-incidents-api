import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Equipamento, Incidente

# Puxa a URL do banco das variáveis de ambiente (Railway)
DATABASE_URL = os.getenv("DATABASE_URL")

# Se estiver rodando local sem DB configurado, usa um SQLite temporário
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="NOC Management API - Portfolio")

# Cria as tabelas automaticamente no banco de dados
Base.metadata.create_all(bind=engine)

# Dependência para abrir/fechar conexão com o banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "NOC System Online", "docs": "/docs"}

# Rota para cadastrar um novo equipamento
@app.post("/equipamentos/")
def criar_equipamento(hostname: str, ip: str, tipo: str, db: Session = Depends(get_db)):
    db_equip = Equipamento(hostname=hostname, ip_address=ip, tipo=tipo)
    db.add(db_equip)
    db.commit()
    db.refresh(db_equip)
    return db_equip

# Rota para abrir um incidente (Ticket)
@app.post("/incidentes/")
def abrir_incidente(titulo: str, severidade: str, equip_id: int, cliente: str, db: Session = Depends(get_db)):
    novo_incidente = Incidente(
        titulo=titulo, 
        severidade=severidade, 
        equipamento_id=equip_id, 
        cliente_b2b=cliente
    )
    db.add(novo_incidente)
    db.commit()
    db.refresh(novo_incidente)
    return novo_incidente

# Rota para listar todos os incidentes
@app.get("/incidentes/")
def listar_incidentes(db: Session = Depends(get_db)):
    return db.query(Incidente).all()