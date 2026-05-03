from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Equipamento(Base):
    __tablename__ = "equipamentos"
    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, unique=True, index=True)
    ip_address = Column(String)
    tipo = Column(String) # Ex: Roteador, Switch, OLT

class Incidente(Base):
    __tablename__ = "incidentes"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    descricao = Column(Text)
    severidade = Column(String) # Critica, Alta, Media, Baixa
    status = Column(String, default="Aberto") # Aberto, Em Analise, Resolvido
    cliente_b2b = Column(String) # Para simular sua experiência real
    data_abertura = Column(DateTime, default=datetime.datetime.utcnow)
    
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id"))
    equipamento = relationship("Equipamento")