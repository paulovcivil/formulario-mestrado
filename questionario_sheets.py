import json
from datetime import datetime

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Amor da minha vida <3 <3", layout="wide")
st.title("📋 Formulário – Projeto de Pesquisa (Mestrado | Poli-USP)")
st.caption("Preencha e clique em **Enviar**. As respostas serão salvas em uma Google Sheet.")

# Você vai definir isso via Secrets (recomendado) ou ambiente.
SPREADSHEET_ID = st.secrets.get("SPREADSHEET_ID", "")
WORKSHEET_NAME = st.secrets.get("WORKSHEET_NAME", "respostas")  # nome da aba

# -----------------------------
# GOOGLE SHEETS AUTH
# -----------------------------
def get_gspread_client():
    """
    Autentica usando Service Account via st.secrets["gcp_service_account"] (JSON).
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
    """
    Garante que a primeira linha tenha o cabeçalho.
    """
    first_row = ws.row_values(1)
    if not first_row:
        ws.append_row(header, value_input_option="RAW")
    else:
        # Se já existe, não altera (evita bagunça)
        pass

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

    # Define colunas (ordem fixa)
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
        # Extra: salvar o JSON completo (opcional, útil)
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
with st.form("form_projeto", clear_on_submit=False):
    st.header("1️⃣ Identificação Básica")
    c1, c2 = st.columns(2)
    with c1:
        titulo = st.text_input("1. Título provisório")
        orientador = st.text_input("2. Nome do orientador")
    with c2:
        area = st.text_input("3. Área de concentração do programa")
        linha = st.text_input("4. Linha de pesquisa formal do programa")
    vinculo = st.text_area("5. Projeto maior vinculado (FAPESP/CNPq/parceria)?", height=100)

    st.header("2️⃣ Contexto Geral da Pesquisa")
    problema = st.text_area("6. Problema técnico/científico", height=110)
    relevancia = st.text_area("7. Relevância hoje (aplicação, custo, sustentabilidade...)", height=110)

    focos_lista = [
        "Comportamento mecânico",
        "Durabilidade",
        "Modelagem numérica",
        "Dosagem e microestrutura",
        "Aplicações estruturais",
        "Desenvolvimento de metodologia",
        "Outro",
    ]
    foco = st.multiselect("8. Foco principal:", options=focos_lista)
    foco_outro = st.text_input("Se marcou 'Outro', especifique:")

    st.header("3️⃣ Delimitação Técnica")
    delimitacao = st.text_area("9. Delimitação técnica", height=120)
    tipo_estudo = st.radio("10. O estudo será:", ["Experimental", "Numérico", "Teórico", "Experimental + Numérico"])

    st.subheader("Parte experimental")
    ensaios = st.text_area("11a. Ensaios pretendidos", height=90)
    laboratorio = st.text_input("11b. Laboratório disponível (qual)?")
    traco = st.text_input("11c. Traço UHPFRC definido? (sim/não + detalhes)")

    st.subheader("Parte numérica")
    software = st.text_input("12a. Software(s) (ABAQUS/ANSYS/OpenSees/código próprio...)")
    modelo_constitutivo = st.text_input("12b. Modelo constitutivo? (sim/não + ideia)")
    ml = st.text_input("12c. Machine learning? (sim/não + onde faria sentido)")

    st.header("4️⃣ Estado da Arte")
    artigos_base = st.text_area("13. Artigos/referências base", height=110)
    lacuna = st.text_area("14. Lacuna percebida na literatura", height=110)
    origem_tema = st.radio(
        "15. Seu trabalho será:",
        ["Evolução de pesquisa da graduação", "Continuação de projeto do orientador", "Tema novo dentro do grupo"]
    )
    conexao = st.text_area("15b. Conexão com pesquisas anteriores", height=110)

    st.header("5️⃣ Hipóteses e Objetivos")
    hipotese = st.text_area("16. Hipótese central", height=90)
    obj_geral = st.text_area("17. Objetivo geral", height=80)
    obj_especificos = st.text_area("18. Objetivos específicos (3–5)", height=120)

    st.header("6️⃣ Metodologia")
    etapas = st.text_area("19. Etapas técnicas do trabalho", height=120)
    pretende = st.text_area("20. Pretende (paramétrica, comparar, propor modelo, validar norma...)", height=110)

    st.header("7️⃣ Resultados Esperados")
    produtos = st.text_area("21. Produtos finais esperados", height=110)
    contribuicao = st.text_area("22. Contribuição científica principal", height=110)

    st.header("8️⃣ Cronograma")
    c3, c4, c5 = st.columns(3)
    with c3:
        duracao = st.text_input("23. Duração prevista (meses)", value="24")
    with c4:
        qualif = st.text_input("24. Qualificação (meses)")
    with c5:
        artigo = st.text_input("25. Submeter artigo antes da defesa? (sim/não + quando)")

    st.header("9️⃣ Infraestrutura e Viabilidade")
    conversou = st.text_input("26. Viabilidade com orientador (sim/não + notas)")
    financiamento = st.text_input("27. Financiamento previsto (bolsa/agência/projeto)")
    parceria = st.text_input("28. Parceria com empresa?")

    st.header("🔟 Diferencial do Candidato")
    formacao = st.text_area("29. Como sua formação contribui", height=100)
    skills = st.text_area("30. Como seu conhecimento (Python/métodos numéricos...) agrega", height=100)
    futuro_ia = st.text_input("31. Integrar IA/modelagem avançada futuramente? (sim/não + como)")

    enviado = st.form_submit_button("📩 Enviar para a planilha")

if enviado:
    payload = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "titulo": titulo,
        "orientador": orientador,
        "area_concentracao": area,
        "linha_pesquisa": linha,
        "vinculo_projeto_maior": vinculo,
        "problema": problema,
        "relevancia": relevancia,
        "foco": foco,
        "foco_outro": foco_outro,
        "delimitacao": delimitacao,
        "tipo_estudo": tipo_estudo,
        "ensaios": ensaios,
        "laboratorio": laboratorio,
        "traco_uhpfrc": traco,
        "software": software,
        "modelo_constitutivo": modelo_constitutivo,
        "ml": ml,
        "artigos_base": artigos_base,
        "lacuna": lacuna,
        "origem_tema": origem_tema,
        "conexao_pesquisas": conexao,
        "hipotese": hipotese,
        "objetivo_geral": obj_geral,
        "objetivos_especificos": obj_especificos,
        "etapas": etapas,
        "pretende": pretende,
        "produtos": produtos,
        "contribuicao": contribuicao,
        "duracao_meses": duracao,
        "qualificacao_meses": qualif,
        "submissao_artigo": artigo,
        "viabilidade_orientador": conversou,
        "financiamento": financiamento,
        "parceria": parceria,
        "formacao_contribuicao": formacao,
        "skills_contribuicao": skills,
        "futuro_ia": futuro_ia,
    }

    try:
        append_response_to_sheet(payload)
        st.success("✅ Enviado! Sua resposta foi salva na planilha.")
    except Exception as e:
        st.error("❌ Falha ao enviar para a planilha.")
        st.exception(e)

