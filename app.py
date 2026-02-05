import streamlit as st
import json
import os
import re
import uuid

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="LegalDesk Pro",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARQUIVO_DADOS = "dados_legaldesk.json"

# --- DADOS PADRÃO ---
LINKS_PADRAO = {
    "fiscal": [
        {"id": "f1", "nome": "🏢 Certidão Federal", "url": "https://servicos.receitafederal.gov.br/servico/certidoes/#/home/cnpj", "fav": False},
        {"id": "f2", "nome": "🏢 Receita (CNPJ)", "url": "https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/cnpjreva_solicitacao.asp", "fav": True},
        {"id": "f3", "nome": "🏦 Caixa (FGTS)", "url": "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf", "fav": False},
        {"id": "f4", "nome": "🏙️ Pref. SP (DUC)", "url": "https://duc.prefeitura.sp.gov.br/certidoes/forms_anonimo/frmConsultaEmissaoCertificado.aspx", "fav": False},
        {"id": "f5", "nome": "📍 Sefaz SP (Estadual)", "url": "https://www10.fazenda.sp.gov.br/CertidaoNegativaDeb/Pages/EmissaoCertidaoNegativa.aspx", "fav": False},
        {"id": "f6", "nome": "📂 Jucesp (Ficha)", "url": "https://www.jucesponline.sp.gov.br/Default.aspx", "fav": True}
    ],
    "trabalhista": [
        {"id": "t1", "nome": "👷 TST (CNDT Nacional)", "url": "https://cndt-certidao.tst.jus.br/inicio.faces", "fav": False},
        {"id": "t2", "nome": "⚖️ TRT-2 (Regional SP)", "url": "https://pje.trt2.jus.br/certidoes/trabalhista/emissao", "fav": False}
    ],
    "juridico": [
        {"id": "j1", "nome": "🏛️ Falência TJSP", "url": "https://esaj.tjsp.jus.br/sco/abrirCadastro.do", "fav": False},
        {"id": "j2", "nome": "⚖️ TRF-3 (Federal)", "url": "https://web.trf3.jus.br/certidao-regional/CertidaoCivelEleitoralCriminal/SolicitarDadosCertidao", "fav": False},
        {"id": "j3", "nome": "🚫 Protesto (IEPTB)", "url": "https://protestosp.com.br/consulta-de-protesto", "fav": True}
    ]
}

# --- FUNÇÕES DE GERENCIAMENTO DE DADOS ---
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return LINKS_PADRAO
    return LINKS_PADRAO

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def toggle_favorito(categoria, index):
    st.session_state.dados[categoria][index]['fav'] = not st.session_state.dados[categoria][index]['fav']
    salvar_dados(st.session_state.dados)

def formatar_cnpjs_texto(texto):
    if not texto: return ""
    # Regex para encontrar sequências de 14 dígitos e formatar
    return re.sub(r'\b(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})\b', r'\1.\2.\3/\4-\5', texto)

# --- INICIALIZAÇÃO DO ESTADO ---
if 'dados' not in st.session_state:
    st.session_state.dados = carregar_dados()

if 'bloco_notas' not in st.session_state:
    st.session_state.bloco_notas = ""

# --- CSS PERSONALIZADO (Visual Pro) ---
st.markdown("""
    <style>
    /* Remove padding excessivo do topo */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* Estilo dos Cards */
    .link-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .link-card:hover { border-color: #3b82f6; transform: translateY(-2px); }
    
    /* Botões personalizados */
    div.stButton > button { width: 100%; border-radius: 6px; }
    
    /* Título */
    h1 { color: #1e293b; font-family: 'Inter', sans-serif; }
    h3 { color: #475569; font-size: 1.1rem !important; }
    
    /* Dark mode adjustments (automático do Streamlit, mas forçando contraste) */
    @media (prefers-color-scheme: dark) {
        .link-card { background-color: #1e293b; border-color: #334155; }
        h1 { color: #f1f5f9; }
        h3 { color: #cbd5e1; }
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Bloco de Notas e Gestão) ---
with st.sidebar:
    st.title("📝 Bloco Rápido")
    
    # Bloco de Notas Inteligente
    texto_notas = st.text_area(
        "Cole CNPJs aqui (sem formatação)", 
        value=st.session_state.bloco_notas, 
        height=200,
        help="Cole números soltos (ex: 12345678000199) e clique em formatar."
    )
    st.session_state.bloco_notas = texto_notas

    col_fmt, col_limp = st.columns(2)
    if col_fmt.button("✨ Formatar CNPJs"):
        st.session_state.bloco_notas = formatar_cnpjs_texto(texto_notas)
        st.rerun()
    
    if col_limp.button("🗑️ Limpar"):
        st.session_state.bloco_notas = ""
        st.rerun()

    st.markdown("---")
    st.subheader("⚙️ Adicionar Link")
    
    with st.form("novo_link"):
        cat_opt = st.selectbox("Categoria", ["fiscal", "trabalhista", "juridico"])
        nome_new = st.text_input("Nome do Site")
        url_new = st.text_input("URL (Link)")
        submitted = st.form_submit_button("Salvar Novo Link")
        
        if submitted and nome_new and url_new:
            novo_item = {
                "id": str(uuid.uuid4()),
                "nome": nome_new,
                "url": url_new,
                "fav": False
            }
            st.session_state.dados[cat_opt].append(novo_item)
            salvar_dados(st.session_state.dados)
            st.success("Adicionado!")
            st.rerun()

# --- ÁREA PRINCIPAL ---

# Cabeçalho e Busca
c1, c2, c3 = st.columns([3, 2, 1])
with c1:
    st.title("LegalDesk Pro")
with c2:
    termo_busca = st.text_input("🔍 Buscar (nome ou link)", placeholder="Ex: receita, tjsp...")
with c3:
    st.write("") # Espaçamento
    st.write("") 
    ver_favoritos = st.toggle("⭐ Só Favoritos")

st.markdown("---")

# Função para renderizar categoria
def renderizar_categoria(titulo, chave_json, cor_icone):
    links = st.session_state.dados.get(chave_json, [])
    
    # Filtragem
    links_filtrados = []
    for idx, link in enumerate(links):
        match_busca = (termo_busca.lower() in link['nome'].lower()) or (termo_busca.lower() in link['url'].lower())
        match_fav = link['fav'] if ver_favoritos else True
        
        if match_busca and match_fav:
            links_filtrados.append((idx, link))
    
    if not links_filtrados and termo_busca:
        return # Não mostra a categoria se a busca não encontrou nada nela

    if not links_filtrados and ver_favoritos:
         return # Não mostra se não tem favoritos nesta categoria

    st.subheader(f"{cor_icone} {titulo}")
    
    # Grid Responsivo (usando colunas do Streamlit)
    # Quebra em linhas de 3 colunas
    cols_por_linha = 3
    for i in range(0, len(links_filtrados), cols_por_linha):
        cols = st.columns(cols_por_linha)
        for j in range(cols_por_linha):
            if i + j < len(links_filtrados):
                idx_real, item = links_filtrados[i+j]
                
                with cols[j]:
                    # Container para simular o Card
                    with st.container(border=True):
                        # Linha 1: Nome e Favorito
                        c_nome, c_fav = st.columns([0.8, 0.2])
                        c_nome.markdown(f"**{item['nome']}**")
                        
                        icone_fav = "⭐" if item['fav'] else "☆"
                        if c_fav.button(icone_fav, key=f"fav_{item['id']}", help="Favoritar"):
                            toggle_favorito(chave_json, idx_real)
                            st.rerun()
                        
                        # Linha 2: Botão de Acesso
                        st.link_button("Acessar Site 🔗", item['url'], use_container_width=True)

# Renderiza as seções
renderizar_categoria("Regularidade Fiscal", "fiscal", "📗")
renderizar_categoria("Trabalhista", "trabalhista", "📘")
renderizar_categoria("Jurídico & Protestos", "juridico", "⚖️")

# Mensagem se nada for encontrado
todos_vazios = True
for cat in ["fiscal", "trabalhista", "juridico"]:
    # Lógica simplificada para checar se algo foi exibido
    items = st.session_state.dados[cat]
    for item in items:
        if (termo_busca.lower() in item['nome'].lower() or termo_busca.lower() in item['url'].lower()) and (item['fav'] if ver_favoritos else True):
            todos_vazios = False
            break

if todos_vazios:
    st.warning("Nenhum link encontrado com os filtros atuais.")

# Rodapé
st.markdown("---")
st.caption("LegalDesk Pro v2.0 - Desenvolvido em Python/Streamlit")