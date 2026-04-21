import fitz
import re
import argparse

class PDFInjectionDetector:
    def __init__(self):
        self.rules = {
            "Instrucción de Ignorar": r"(?i)ignore (all )?previous instructions",
            "Sobrescritura de Sistema": r"(?i)system override",
            "Cambio de Rol": r"(?i)you are now a",
            "Comando de Olvido": r"(?i)forget everything you know",
        }

    def scan(self, pdf_path):
        print(f"\nEscaneando: {pdf_path}")
        print("=" * 50)
        
        full_content = ""
        threats_found = 0
        hidden_text_detected = False

        try:
            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc, 1):
                    blocks = page.get_text("dict")["blocks"]
                    for b in blocks:
                        if "lines" in b:
                            for l in b["lines"]:
                                for s in l["spans"]:
                                    text = s['text'].strip()
                                    if not text: continue
                                    
                                    # Detectar Blanco (16777215) o colores muy claros
                                    if s['color'] == 16777215:
                                        print(f"[CRÍTICO] Texto invisible detectado en Pág {page_num}: '{text}'")
                                        hidden_text_detected = True
                                        threats_found += 1
                                    
                                    full_content += text + " "

            # Analizar el contenido total con las RegEx
            for name, pattern in self.rules.items():
                matches = re.findall(pattern, full_content)
                if matches:
                    print(f"[ALERTA] Patrón lógico detectado: {name}")
                    threats_found += len(matches)

            if threats_found == 0:
                print("Resultado: Documento limpio.")
            else:
                print(f"\nRESUMEN: Se encontraron {threats_found} posibles vectores de ataque.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("archivo")
    args = parser.parse_args()
    PDFInjectionDetector().scan(args.archivo)
