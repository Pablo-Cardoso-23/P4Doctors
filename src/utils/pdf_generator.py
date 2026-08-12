from fpdf import FPDF
import tempfile
import unicodedata
from datetime import datetime

def remover_acentos(texto):
    if not texto:
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn')

def gerar_pdf_prontuario(nome_medico, nome_paciente, data_atend, local, tipo, relatorio):
    try:
        dt_obj = datetime.strptime(data_atend, "%Y-%m-%d %H:%M:%S")
        data_formatada = dt_obj.strftime("%d/%m/%Y as %H:%M")
    except ValueError:
        data_formatada = data_atend

    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, txt="Prontuário Médico - P4 Health", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(40, 8, txt="Médico(a):", ln=False)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, txt=remover_acentos(nome_medico), ln=True)
    
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(40, 8, txt="Paciente:", ln=False)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, txt=remover_acentos(nome_paciente), ln=True)
    
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(40, 8, txt="Data:", ln=False)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, txt=remover_acentos(data_formatada), ln=True)
    
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(40, 8, txt="Local:", ln=False)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, txt=remover_acentos(local), ln=True)
    
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(40, 8, txt="Tipo:", ln=False)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, txt=remover_acentos(tipo), ln=True)
    
    pdf.ln(10)
    
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 8, txt="Evolução Clínica / Relatório:", ln=True)
    pdf.set_font("Arial", size=12)
    
    texto_relatorio = relatorio if relatorio and str(relatorio).strip() else "Nenhuma observação registrada."
    texto_relatorio = remover_acentos(texto_relatorio)
    
    pdf.multi_cell(0, 8, txt=texto_relatorio)
    
    pdf.ln(30)
    
    pdf.cell(0, 8, txt="_________________________________________________", ln=True, align="C")
    pdf.cell(0, 8, txt=f"Assinatura - {remover_acentos(nome_medico)}", ln=True, align="C")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            pdf_bytes = f.read()
            
    return pdf_bytes