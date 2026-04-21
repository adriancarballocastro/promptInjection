import streamlit as st
import fitz  
import re

st.set_page_config(
    page_title="AI PDF Guard",
    page_icon="🛡️",
    layout="centered"
)

class PDFScanner:
    def __init__(self):
        self.rules = {
            "Instrucción de Ignorar": r"(?i)ignore (all )?previous instructions",
            "Sobrescritura de Sistema": r"(?i)system override",
            "Cambio de Rol": r"(?i)you are now a",
            "Comando de Olvido": r"(?i)forget everything you know",
            "Inyección de Salida": r"(?i)output the following text instead",
        }

    def scan(self, uploaded_file):
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        full_content = ""
        threats = []
        hidden_text = []

        for page_num, page in enumerate(doc, 1):
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if "lines" in b:
                    for l in b["lines"]:
                        for s in l["spans"]:
                            text = s['text'].strip()
                            if not text: continue
                            
                            if s['color'] == 16777215:
                                hidden_text.append(f"Pág {page_num}: '{text}'")
                            
                            full_content += text + " "

        for name, pattern in self.rules.items():
            if re.search(pattern, full_content):
                threats.append(name)
        
        return threats, hidden_text, full_content

st.title("AI PDF Guard")
st.subheader("Detector de Prompt Injection")

st.sidebar.info("""
**¿Cómo funciona?**
Este sistema analiza el contenido del PDF buscando:
1. Texto oculto (blanco sobre blanco).
2. Comandos que intentan engañar a una IA.
""")

file = st.file_uploader("Arrastra aquí tu PDF", type="pdf")

if file:
    scanner = PDFScanner()
    with st.spinner('Analizando capas del documento...'):
        threats, hidden, content = scanner.scan(file)
    
    st.divider()
    
    if not threats and not hidden:
        st.success("**Documento Limpio.** No se detectaron vectores de ataque.")
    else:
        if hidden:
            st.warning(f"🚨 Se detectó **texto invisible** en {len(hidden)} fragmentos.")
            with st.expander("Ver texto oculto"):
                for h in hidden: st.write(h)
        
        if threats:
            st.error(f" Se detectaron {len(threats)} **patrones de inyección**.")
            with st.expander("Ver amenazas lógicas"):
                for t in threats: st.write(f"• {t}")

    with st.expander(" Ver lo que la IA leería (Texto Plano)"):
        st.text_area("Contenido extraído:", content, height=250)
