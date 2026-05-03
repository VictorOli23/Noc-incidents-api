import os
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Incidente, Equipamento

# Configuração do Banco de Dados (agora apontando para o Neon via Variável de Ambiente)
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="NOC Management API")

# Cria as tabelas automaticamente
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- CÓDIGO DO DASHBOARD FRONT-END ---
html_dashboard = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard NOC</title>
    <!-- Tailwind CSS para deixar o visual moderno sem precisar de arquivos extras -->
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 text-slate-800 font-sans p-8">
    <div class="max-w-5xl mx-auto">
        <header class="flex justify-between items-center mb-8 bg-slate-900 text-white p-6 rounded-lg shadow-lg">
            <div>
                <h1 class="text-3xl font-bold flex items-center gap-2">
                    🖥️ NOC Dashboard
                </h1>
                <p class="text-slate-300 mt-1">Monitoramento de Incidentes em Tempo Real</p>
            </div>
            <a href="/docs" class="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded font-semibold transition">
                Acessar API (Swagger)
            </a>
        </header>

        <div class="bg-white p-6 rounded-lg shadow-md">
            <h2 class="text-xl font-bold mb-4 border-b pb-2">Incidentes Ativos</h2>
            
            <div class="overflow-x-auto">
                <table class="min-w-full text-left text-sm">
                    <thead class="bg-slate-50 text-slate-600">
                        <tr>
                            <th class="px-6 py-3 border-b font-semibold">ID Ticket</th>
                            <th class="px-6 py-3 border-b font-semibold">Título do Incidente</th>
                            <th class="px-6 py-3 border-b font-semibold">Severidade</th>
                            <th class="px-6 py-3 border-b font-semibold">Cliente B2B</th>
                            <th class="px-6 py-3 border-b font-semibold">Data</th>
                        </tr>
                    </thead>
                    <tbody id="tabela-incidentes" class="divide-y divide-slate-100">
                        <!-- O Javascript vai inserir os dados aqui -->
                        <tr><td colspan="5" class="text-center py-4 text-slate-400">Carregando dados...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Função para buscar os dados da própria API
        fetch('/incidentes/')
            .then(response => response.json())
            .then(data => {
                const tbody = document.getElementById('tabela-incidentes');
                tbody.innerHTML = ''; // Limpa o "Carregando"

                if(data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-6 text-slate-500 font-medium">Nenhum incidente ativo no momento. ✅</td></tr>';
                    return;
                }

                data.forEach(incidente => {
                    // Formata a cor da severidade
                    let corSeveridade = 'bg-slate-200 text-slate-700'; // Default
                    if(incidente.severidade.toLowerCase() === 'critica' || incidente.severidade.toLowerCase() === 'crítica') {
                        corSeveridade = 'bg-red-100 text-red-700 font-bold';
                    } else if (incidente.severidade.toLowerCase() === 'alta') {
                        corSeveridade = 'bg-orange-100 text-orange-700 font-semibold';
                    } else if (incidente.severidade.toLowerCase() === 'media' || incidente.severidade.toLowerCase() === 'média') {
                        corSeveridade = 'bg-yellow-100 text-yellow-700';
                    }

                    // Formata a data
                    let dataFormatada = new Date(incidente.data_abertura).toLocaleString('pt-BR');

                    tbody.innerHTML += `
                        <tr class="hover:bg-slate-50 transition">
                            <td class="px-6 py-4 font-mono text-xs">#${incidente.id}</td>
                            <td class="px-6 py-4 font-medium">${incidente.titulo}</td>
                            <td class="px-6 py-4">
                                <span class="px-2 py-1 rounded-full text-xs ${corSeveridade}">${incidente.severidade}</span>
                            </td>
                            <td class="px-6 py-4">${incidente.cliente_b2b}</td>
                            <td class="px-6 py-4 text-slate-500 text-xs">${dataFormatada}</td>
                        </tr>
                    `;
                });
            })
            .catch(error => {
                document.getElementById('tabela-incidentes').innerHTML = '<tr><td colspan="5" class="text-center py-4 text-red-500">Erro ao carregar dados da API.</td></tr>';
            });
    </script>
</body>
</html>
"""

# --- ROTAS DA API ---

@app.get("/", response_class=HTMLResponse)
def dashboard():
    # Retorna o painel visual quando acessar a URL principal
    return HTMLResponse(content=html_dashboard, status_code=200)

@app.get("/incidentes/")
def listar_incidentes(db: Session = Depends(get_db)):
    return db.query(Incidente).all()

@app.post("/equipamentos/")
def criar_equipamento(hostname: str, ip: str, tipo: str, db: Session = Depends(get_db)):
    db_equip = Equipamento(hostname=hostname, ip_address=ip, tipo=tipo)
    db.add(db_equip)
    db.commit()
    db.refresh(db_equip)
    return db_equip

@app.post("/incidentes/")
def abrir_incidente(titulo: str, severidade: str, equip_id: int, cliente: str, db: Session = Depends(get_db)):
    novo_incidente = Incidente(titulo=titulo, severidade=severidade, equipamento_id=equip_id, cliente_b2b=cliente)
    db.add(novo_incidente)
    db.commit()
    db.refresh(novo_incidente)
    return novo_incidente
