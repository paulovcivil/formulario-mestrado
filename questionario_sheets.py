# questionario_sheets.py
# Streamlit form -> Google Sheets (Service Account via Streamlit Secrets)
# Adiciona botão explícito "Limpar formulário" (sem quebrar o app / session_state)
#
# Deploy: Streamlit Cloud + Secrets:
#   SPREADSHEET_ID = "..."
#   WORKSHEET_NAME = "respostas"
#   [gcp_service_account] ... (service account)

import json
from datetime import datetime

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Formulário Mestrado", layout="wide")
st.title("📋 Formulário Mestrado - Escola Politécnica USP")
st.caption("Preencha e clique em **Enviar**. As respostas serão salvas em uma Google Sheet.")

SPREADSHEET_ID = st.secrets.get("SPREADSHEET_ID", "")
WORKSHEET_NAME = st.secrets.get("WORKSHEET_NAME", "respostas")  # nome da aba

if "form_version" not in st.session_state:
    st.session_state["form_version"] = 0

def limpar_formulario() -> None:
    # limpa valores dos widgets
    for k in FORM_KEYS:
        st.session_state.pop(k, None)
    # força recriação do form (zera o estado no frontend)
    st.session_state["form_version"] += 1

# -----------------------------
# FORM KEYS (para limpar com segurança)
# -----------------------------
FORM_KEYS = [
    "titulo", "orientador", "area", "linha", "vinculo",
    "problema", "relevancia", "foco", "foco_outro",
    "delimitacao", "tipo_estudo",
    "ensaios", "laboratorio", "traco",
    "software", "modelo_constitutivo", "ml",
    "artigos_base", "lacuna", "origem_tema", "conexao",
    "hipotese", "obj_geral", "obj_especificos",
    "etapas", "pretende",
    "produtos", "contribuicao",
    "duracao", "qualif", "artigo",
    "conversou", "financiamento", "parceria",
    "formacao", "skills", "futuro_ia",
]

def limpar_formulario() -> None:
    """Remove apenas os campos do formulário do session_state (sem quebrar coisas internas do Streamlit)."""
    for k in FORM_KEYS:
        if k in st.session_state:
            del st.session_state[k]

# -----------------------------
# GOOGLE SHEETS AUTH
# -----------------------------
def get_gspread_client():
    """
    Autentica usando Service Account via st.secrets["gcp_service_account"] (TOML -> dict).
    """
    if "gcp_service_account" not in st.secrets:
        st.error("Credenciais não configuradas. Falta `gcp_service_account` em st.secrets.")
        st.stop()

    service_account_info = dict(st.secrets["gcp_service_account"])

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    return gspread.authorize(creds)

def ensure_header(ws, header):
    """Garante que a primeira linha tenha o cabeçalho."""
    first_row = ws.row_values(1)
    if not first_row:
        ws.append_row(header, value_input_option="RAW")

def append_response_to_sheet(payload: dict):
    gc = get_gspread_client()

    if not SPREADSHEET_ID:
        st.error("Falta configurar `SPREADSHEET_ID` em st.secrets.")
        st.stop()

    sh = gc.open_by_key(SPREADSHEET_ID)

    # Cria/abre a aba
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=2000, cols=80)

    header = [
        "timestamp",
        "titulo",
        "orientador",
        "area_concentracao",
        "linha_pesquisa",
        "vinculo_projeto_maior",
        "problema",
        "relevancia",
        "foco",
        "foco_outro",
        "delimitacao",
        "tipo_estudo",
        "ensaios",
        "laboratorio",
        "traco_uhpfrc",
        "software",
        "modelo_constitutivo",
        "ml",
        "artigos_base",
        "lacuna",
        "origem_tema",
        "conexao_pesquisas",
        "hipotese",
        "objetivo_geral",
        "objetivos_especificos",
        "etapas",
        "pretende",
        "produtos",
        "contribuicao",
        "duracao_meses",
        "qualificacao_meses",
        "submissao_artigo",
        "viabilidade_orientador",
        "financiamento",
        "parceria",
        "formacao_contribuicao",
        "skills_contribuicao",
        "futuro_ia",
        "payload_json",
    ]
    ensure_header(ws, header)

    row = [
        payload.get("timestamp", ""),
        payload.get("titulo", ""),
        payload.get("orientador", ""),
        payload.get("area_concentracao", ""),
        payload.get("linha_pesquisa", ""),
        payload.get("vinculo_projeto_maior", ""),
        payload.get("problema", ""),
        payload.get("relevancia", ""),
        ", ".join(payload.get("foco", []) or []),
        payload.get("foco_outro", ""),
        payload.get("delimitacao", ""),
        payload.get("tipo_estudo", ""),
        payload.get("ensaios", ""),
        payload.get("laboratorio", ""),
        payload.get("traco_uhpfrc", ""),
        payload.get("software", ""),
        payload.get("modelo_constitutivo", ""),
        payload.get("ml", ""),
        payload.get("artigos_base", ""),
        payload.get("lacuna", ""),
        payload.get("origem_tema", ""),
        payload.get("conexao_pesquisas", ""),
        payload.get("hipotese", ""),
        payload.get("objetivo_geral", ""),
        payload.get("objetivos_especificos", ""),
        payload.get("etapas", ""),
        payload.get("pretende", ""),
        payload.get("produtos", ""),
        payload.get("contribuicao", ""),
        payload.get("duracao_meses", ""),
        payload.get("qualificacao_meses", ""),
        payload.get("submissao_artigo", ""),
        payload.get("viabilidade_orientador", ""),
        payload.get("financiamento", ""),
        payload.get("parceria", ""),
        payload.get("formacao_contribuicao", ""),
        payload.get("skills_contribuicao", ""),
        payload.get("futuro_ia", ""),
        json.dumps(payload, ensure_ascii=False),
    ]

    ws.append_row(row, value_input_option="RAW")

# -----------------------------
# FORM
# -----------------------------
focos_lista = [
    "Comportamento mecânico",
    "Durabilidade",
    "Modelagem numérica",
    "Dosagem e microestrutura",
    "Aplicações estruturais",
    "Desenvolvimento de metodologia",
    "Outro",
]

with st.form(f"form_projeto_{st.session_state['form_version']}", clear_on_submit=True):
    st.header("1️⃣ Identificação Básica")
    c1, c2 = st.columns(2)
    with c1:
        titulo = st.text_input("1. Título provisório", key="titulo")
        orientador = st.text_input("2. Nome do orientador", key="orientador")
    with c2:
        area = st.text_input("3. Área de concentração do programa", key="area")
        linha = st.text_input("4. Linha de pesquisa formal do programa", key="linha")
    vinculo = st.text_area("5. Projeto maior vinculado (FAPESP/CNPq/parceria)?", height=100, key="vinculo")

    st.header("2️⃣ Contexto Geral da Pesquisa")
    problema = st.text_area("6. Problema técnico/científico", height=110, key="problema")
    relevancia = st.text_area("7. Relevância hoje (aplicação, custo, sustentabilidade...)", height=110, key="relevancia")

    foco = st.multiselect("8. Foco principal:", options=focos_lista, key="foco")
    foco_outro = st.text_input("Se marcou 'Outro', especifique:", key="foco_outro")

    st.header("3️⃣ Delimitação Técnica")
    delimitacao = st.text_area("9. Delimitação técnica", height=120, key="delimitacao")
    tipo_estudo = st.radio(
        "10. O estudo será:",
        ["Experimental", "Numérico", "Teórico", "Experimental + Numérico"],
        key="tipo_estudo",
    )

    st.subheader("Parte experimental")
    ensaios = st.text_area("11a. Ensaios pretendidos", height=90, key="ensaios")
    laboratorio = st.text_input("11b. Laboratório disponível (qual)?", key="laboratorio")
    traco = st.text_input("11c. Traço UHPFRC definido? (sim/não + detalhes)", key="traco")

    st.subheader("Parte numérica")
    software = st.text_input("12a. Software(s) (ABAQUS/ANSYS/OpenSees/código próprio...)", key="software")
    modelo_constitutivo = st.text_input("12b. Modelo constitutivo? (sim/não + ideia)", key="modelo_constitutivo")
    ml = st.text_input("12c. Machine learning? (sim/não + onde faria sentido)", key="ml")

    st.header("4️⃣ Estado da Arte")
    artigos_base = st.text_area("13. Artigos/referências base", height=110, key="artigos_base")
    lacuna = st.text_area("14. Lacuna percebida na literatura", height=110, key="lacuna")
    origem_tema = st.radio(
        "15. Seu trabalho será:",
        ["Evolução de pesquisa da graduação", "Continuação de projeto do orientador", "Tema novo dentro do grupo"],
        key="origem_tema",
    )
    conexao = st.text_area("15b. Conexão com pesquisas anteriores", height=110, key="conexao")

    st.header("5️⃣ Hipóteses e Objetivos")
    hipotese = st.text_area("16. Hipótese central", height=90, key="hipotese")
    obj_geral = st.text_area("17. Objetivo geral", height=80, key="obj_geral")
    obj_especificos = st.text_area("18. Objetivos específicos (3–5)", height=120, key="obj_especificos")

    st.header("6️⃣ Metodologia")
    etapas = st.text_area("19. Etapas técnicas do trabalho", height=120, key="etapas")
    pretende = st.text_area(
        "20. Pretende (paramétrica, comparar, propor modelo, validar norma...)",
        height=110,
        key="pretende",
    )

    st.header("7️⃣ Resultados Esperados")
    produtos = st.text_area("21. Produtos finais esperados", height=110, key="produtos")
    contribuicao = st.text_area("22. Contribuição científica principal", height=110, key="contribuicao")

    st.header("8️⃣ Cronograma")
    c3, c4, c5 = st.columns(3)
    with c3:
        duracao = st.text_input("23. Duração prevista (meses)", value=st.session_state.get("duracao", "24"), key="duracao")
    with c4:
        qualif = st.text_input("24. Qualificação (meses)", key="qualif")
    with c5:
        artigo = st.text_input("25. Submeter artigo antes da defesa? (sim/não + quando)", key="artigo")

    st.header("9️⃣ Infraestrutura e Viabilidade")
    conversou = st.text_input("26. Viabilidade com orientador (sim/não + notas)", key="conversou")
    financiamento = st.text_input("27. Financiamento previsto (bolsa/agência/projeto)", key="financiamento")
    parceria = st.text_input("28. Parceria com empresa?", key="parceria")

    st.header("🔟 Diferencial do Candidato")
    formacao = st.text_area("29. Como sua formação contribui", height=100, key="formacao")
    skills = st.text_area("30. Como seu conhecimento (Python/métodos numéricos...) agrega", height=100, key="skills")
    futuro_ia = st.text_input("31. Integrar IA/modelagem avançada futuramente? (sim/não + como)", key="futuro_ia")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        enviado = st.form_submit_button("📩 Enviar para a planilha")
    with col_btn2:
        st.form_submit_button("🗑️ Limpar formulário", on_click=limpar_formulario)


# -----------------------------
# ACTIONS
# -----------------------------


if "enviado" in locals() and enviado:
    payload = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "titulo": st.session_state.get("titulo", ""),
        "orientador": st.session_state.get("orientador", ""),
        "area_concentracao": st.session_state.get("area", ""),
        "linha_pesquisa": st.session_state.get("linha", ""),
        "vinculo_projeto_maior": st.session_state.get("vinculo", ""),
        "problema": st.session_state.get("problema", ""),
        "relevancia": st.session_state.get("relevancia", ""),
        "foco": st.session_state.get("foco", []),
        "foco_outro": st.session_state.get("foco_outro", ""),
        "delimitacao": st.session_state.get("delimitacao", ""),
        "tipo_estudo": st.session_state.get("tipo_estudo", ""),
        "ensaios": st.session_state.get("ensaios", ""),
        "laboratorio": st.session_state.get("laboratorio", ""),
        "traco_uhpfrc": st.session_state.get("traco", ""),
        "software": st.session_state.get("software", ""),
        "modelo_constitutivo": st.session_state.get("modelo_constitutivo", ""),
        "ml": st.session_state.get("ml", ""),
        "artigos_base": st.session_state.get("artigos_base", ""),
        "lacuna": st.session_state.get("lacuna", ""),
        "origem_tema": st.session_state.get("origem_tema", ""),
        "conexao_pesquisas": st.session_state.get("conexao", ""),
        "hipotese": st.session_state.get("hipotese", ""),
        "objetivo_geral": st.session_state.get("obj_geral", ""),
        "objetivos_especificos": st.session_state.get("obj_especificos", ""),
        "etapas": st.session_state.get("etapas", ""),
        "pretende": st.session_state.get("pretende", ""),
        "produtos": st.session_state.get("produtos", ""),
        "contribuicao": st.session_state.get("contribuicao", ""),
        "duracao_meses": st.session_state.get("duracao", ""),
        "qualificacao_meses": st.session_state.get("qualif", ""),
        "submissao_artigo": st.session_state.get("artigo", ""),
        "viabilidade_orientador": st.session_state.get("conversou", ""),
        "financiamento": st.session_state.get("financiamento", ""),
        "parceria": st.session_state.get("parceria", ""),
        "formacao_contribuicao": st.session_state.get("formacao", ""),
        "skills_contribuicao": st.session_state.get("skills", ""),
        "futuro_ia": st.session_state.get("futuro_ia", ""),
    }

    try:
        append_response_to_sheet(payload)
        st.success("✅ Enviado! Sua resposta foi salva na planilha.")
        # Se você quiser limpar automaticamente também após enviar, descomente:
        limpar_formulario()
        st.rerun()
    except Exception as e:
        st.error("❌ Falha ao enviar para a planilha.")
        st.exception(e)





