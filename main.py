import os
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Incidente, Equipamento

# Configuração do Banco de Dados
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

# --- FRONTEND EVOLUÍDO (HTML + TAILWIND + LUCIDE ICONS) ---
html_dashboard = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOC Command Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); }
    </style>
</head>
<body class="bg-[#0f172a] text-slate-200 min-h-screen">
    <div class="flex">
        <!-- Barra Lateral Minimalista -->
        <aside class="w-20 min-h-screen bg-[#1e293b] flex flex-col items-center py-8 border-r border-slate-700/50">
            <div class="p-3 bg-blue-600 rounded-xl mb-10 shadow-lg shadow-blue-500/20">
                <i data-lucide="activity" class="text-white"></i>
            </div>
            <nav class="space-y-8">
                <i data-lucide="layout-dashboard" class="text-blue-400 cursor-pointer"></i>
                <i data-lucide="server" class="text-slate-500 hover:text-white cursor-pointer transition"></i>
                <i data-lucide="alert-triangle" class="text-slate-500 hover:text-white cursor-pointer transition"></i>
            </nav>
        </aside>

        <!-- Conteúdo Principal -->
        <main class="flex-1 p-8">
            <header class="flex justify-between items-center mb-10">
                <div>
                    <h1 class="text-3xl font-bold tracking-tight">NOC Command Center</h1>
                    <p class="text-slate-400 mt-1">Status operacional da infraestrutura global</p>
                </div>
                <div class="flex gap-4">
                    <button onclick="location.reload()" class="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition text-sm">
                        <i data-lucide="refresh-cw" class="w-4 h-4"></i> Atualizar
                    </button>
                    <a href="/docs" class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold transition text-sm shadow-lg shadow-blue-500/20">
                        <i data-lucide="terminal" class="w-4 h-4"></i> API Console
                    </a>
                </div>
            </header>

            <!-- Grid de Métricas (Cards) -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10 text-white">
                <div class="bg-[#1e293b] p-6 rounded-2xl border border-slate-700/50">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2 bg-blue-500/10 rounded-lg"><i data-lucide="ticket" class="text-blue-500 w-5 h-5"></i></div>
                        <span class="text-xs text-slate-400 font-medium uppercase tracking-wider">Total Ativos</span>
                    </div>
                    <h3 class="text-3xl font-bold" id="metric-total">--</h3>
                </div>
                <div class="bg-[#1e293b] p-6 rounded-2xl border border-slate-700/50 border-l-4 border-l-red-500">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2 bg-red-500/10 rounded-lg"><i data-lucide="zap" class="text-red-500 w-5 h-5"></i></div>
                        <span class="text-xs text-slate-400 font-medium uppercase tracking-wider">Severidade Crítica</span>
                    </div>
                    <h3 class="text-3xl font-bold text-red-400" id="metric-critica">--</h3>
                </div>
                <div class="bg-[#1e293b] p-6 rounded-2xl border border-slate-700/50 border-l-4 border-l-orange-500">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2 bg-orange-500/10 rounded-lg"><i data-lucide="alert-circle" class="text-orange-500 w-5 h-5"></i></div>
                        <span class="text-xs text-slate-400 font-medium uppercase tracking-wider">Severidade Alta</span>
                    </div>
                    <h3 class="text-3xl font-bold text-orange-400" id="metric-alta">--</h3>
                </div>
                <div class="bg-[#1e293b] p-6 rounded-2xl border border-slate-700/50">
                    <div class="flex justify-between items-start mb-4">
                        <div class="p-2 bg-emerald-500/10 rounded-lg"><i data-lucide="shield-check" class="text-emerald-500 w-5 h-5"></i></div>
                        <span class="text-xs text-slate-400 font-medium uppercase tracking-wider">Clientes B2B</span>
                    </div>
                    <h3 class="text-3xl font-bold text-emerald-400" id="metric-clientes">--</h3>
                </div>
            </div>

            <!-- Tabela de Incidentes -->
            <div class="bg-[#1e293b] rounded-2xl border border-slate-700/50 overflow-hidden">
                <div class="p-6 border-b border-slate-700/50 flex justify-between items-center">
                    <h2 class="text-xl font-bold">Monitoramento em Tempo Real</h2>
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                        <span class="text-xs text-slate-400 uppercase font-semibold">Live System</span>
                    </div>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left">
                        <thead class="bg-slate-800/50 text-slate-400 text-xs uppercase tracking-widest font-bold">
                            <tr>
                                <th class="px-8 py-4">Status</th>
                                <th class="px-8 py-4">Incidente / Descrição</th>
                                <th class="px-8 py-4 text-center">Severidade</th>
                                <th class="px-8 py-4">Cliente B2B</th>
                                <th class="px-8 py-4">Registrado em</th>
                            </tr>
                        </thead>
                        <tbody id="tabela-incidentes" class="text-sm divide-y divide-slate-700/50">
                            <!-- Inserido via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <script>
        lucide.createIcons();

        fetch('/incidentes/')
            .then(response => response.json())
            .then(data => {
                const tbody = document.getElementById('tabela-incidentes');
                tbody.innerHTML = '';

                // Atualiza Métricas
                document.getElementById('metric-total').innerText = data.length;
                document.getElementById('metric-critica').innerText = data.filter(i => i.severidade.toLowerCase().includes('crit')).length;
                document.getElementById('metric-alta').innerText = data.filter(i => i.severidade.toLowerCase() === 'alta').length;
                document.getElementById('metric-clientes').innerText = [...new Set(data.map(i => i.cliente_b2b))].length;

                if(data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-20 text-slate-500 font-medium">Nenhum incidente ativo. Infraestrutura saudável. ✅</td></tr>';
                    return;
                }

                data.forEach(incidente => {
                    let badgeClass = 'bg-slate-500/20 text-slate-400';
                    let dotClass = 'bg-slate-400';
                    
                    if(incidente.severidade.toLowerCase().includes('crit')) {
                        badgeClass = 'bg-red-500/10 text-red-500 border border-red-500/20';
                        dotClass = 'bg-red-500';
                    } else if (incidente.severidade.toLowerCase() === 'alta') {
                        badgeClass = 'bg-orange-500/10 text-orange-500 border border-orange-500/20';
                        dotClass = 'bg-orange-500';
                    } else if (incidente.severidade.toLowerCase().includes('med')) {
                        badgeClass = 'bg-yellow-500/10 text-yellow-500 border border-yellow-500/20';
                        dotClass = 'bg-yellow-500';
                    }

                    const dataFormatada = new Date(incidente.data_abertura).toLocaleString('pt-BR');

                    tbody.innerHTML += `
                        <tr class="hover:bg-slate-800/30 transition group">
                            <td class="px-8 py-5">
                                <div class="flex items-center gap-3">
                                    <span class="w-2 h-2 rounded-full ${dotClass}"></span>
                                    <span class="font-mono text-xs text-slate-500">ID-${incidente.id}</span>
                                </div>
                            </td>
                            <td class="px-8 py-5 font-semibold text-slate-200">
                                ${incidente.titulo}
                            </td>
                            <td class="px-8 py-5 text-center">
                                <span class="px-3 py-1 rounded-md text-[10px] uppercase font-black ${badgeClass}">
                                    ${incidente.severidade}
                                </span>
                            </td>
                            <td class="px-8 py-5">
                                <div class="flex items-center gap-2">
                                    <i data-lucide="building-2" class="w-4 h-4 text-slate-500"></i>
                                    <span>${incidente.cliente_b2b}</span>
                                </div>
                            </td>
                            <td class="px-8 py-5 text-slate-400 font-mono text-xs">
                                ${dataFormatada}
                            </td>
                        </tr>
                    `;
                });
                lucide.createIcons();
            });
    </script>
</body>
</html>
"""

# --- ROTAS DA API ---

@app.get("/", response_class=HTMLResponse)
def dashboard():
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
