import streamlit as st
import sqlite3
import os
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURAZIONE DATABASE LOCALE (ARCHIVIO UNIVERSALE) ---
def init_db():
    conn = sqlite3.connect("archivio_kernel.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS storico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            materia TEXT,
            task TEXT,
            testo_origine TEXT,
            risultato TEXT
        )
    """)
    conn.commit()
    return conn

db_conn = init_db()

st.set_page_config(page_title="Kernel Agente IA Universale - Google Workspace", layout="wide")

st.title("Kernel Agente IA Universale e Archivio di Stato (Google Workspace)")
st.write("Sistema operativo cognitivo avanzato integrato con le potenzialità di Gemini per tutti gli ordini e gradi scolastici.")

api_key_input = st.text_input("Inserisci la tua API Key di Google AI Studio (Gemini):", type="password")

col1, col2 = st.columns(2)

with col1:
    discipline_scuola = [
        # SCUOLA DELL'INFANZIA
        "--- SCUOLA DELL'INFANZIA ---",
        "Infanzia: Il sé e l'altro (Etica, identità, relazionalità)",
        "Infanzia: Il corpo e il movimento (Sensomotricità e schema corporeo)",
        "Infanzia: Immagini, suoni, colori (Linguaggi creativi e musicali)",
        "Infanzia: I discorsi e le parole (Comunicazione, lingua e narrazione)",
        "Infanzia: La conoscenza del mondo (Esplorazione, ordine e matematica)",
        
        # SCUOLA PRIMARIA
        "--- SCUOLA PRIMARIA ---",
        "Primaria: Italiano / Lingua e Letteratura",
        "Primaria: Matematica e Logica",
        "Primaria: Inglese / Lingua Straniera",
        "Primaria: Storia",
        "Primaria: Geografia",
        "Primaria: Scienze e Tecnologia",
        "Primaria: Arte e Immagine",
        "Primaria: Musica",
        "Primaria: Educazione Motoria / Scienze Motorie",
        "Primaria: Religione Cattolica / Materia Alternativa",
        
        # SCUOLA SECONDARIA DI I E II GRADO + INDIRIZZO MUSICALE
        "--- SECONDARIA E INDIRIZZO MUSICALE ---",
        "1. Italiano / Lingua e Letteratura",
        "2. Matematica",
        "3. Lingua Inglese / Straniere",
        "4. Storia",
        "5. Geografia",
        "6. Scienze Naturali e Biologia",
        "7. Fisica e Chimica",
        "8. Tecnologia / Informatica",
        "9. Arte e Immagine",
        "10. Musica (Generale e Teoria)",
        "10.1. Strumento Musicale: Clarinetto",
        "10.2. Strumento Musicale: Pianoforte",
        "10.3. Strumento Musicale: Chitarra",
        "10.4. Strumento Musicale: Flauto Traverso",
        "11. Educazione Motoria / Scienze Motorie",
        "12. Religione Cattolica",
        "12.1. Attività Alternativa alla Religione Cattolica",
        "13. Educazione Civica / Cittadinanza",
        "14. Contesto Professionale / Aziendale"
    ]
    materia = st.selectbox("1. Ambito Disciplinare / Contesto:", discipline_scuola)

with col2:
    azioni_distinte = [
        "Semplificazione Dedicata BES / DSA (Alta Leggibilità e Glossario)",
        "Adattamento Standard (Classe Intera / Lezione Frontale)",
        "Potenziamento e Approfondimento (Eccellenze / Pensiero Critico)",
        "Generazione Verifiche e Test a Scelta Multipla (con Soluzioni)",
        "Risoluzione e Spiegazione Metodologica Passo-Passo",
        "Creazione Compito di Realtà / Attività Laboratoriale",
        "Sintesi Strutturata e Mappa Concettuale (Punti Chiave)",
        "Analisi Organologica, Tecnica e Acustica dello Strumento",
        "Pianificazione Partitura, Diteggiatura e KPI Esecutivi",
        "Riformattazione Stile, Correzione e Traduzione Professionale"
    ]
    task_operativo = st.selectbox("2. Azione Operativa Specifica (Unica e Isolata):", azioni_distinte)

testo_utente = st.text_area("Inserisci il testo, il capitolo, la consegna o il problema da elaborare:", height=200)

if st.button("Esegui Elaborazione con Gemini e Archivia"):
    if not api_key_input.strip():
        st.error("Inserisci una chiave API di Google valida.")
    elif testo_utente.strip() == "":
        st.warning("Inserisci del testo nel campo sottostante.")
    else:
        with st.spinner("Connessione a Google Gemini e generazione dell'output in corso..."):
            try:
                genai.configure(api_key=api_key_input)
                
                system_instruction = f"""Agisci come un motore cognitivo ed esperto di livello assoluto per la scuola, coprendo ogni ordine e grado (dalla scuola dell'infanzia alla secondaria), con specifica competenza nell'indirizzo musicale (Clarinetto, Pianoforte, Chitarra, Flauto Traverso) e nelle attività di materia alternativa. 
Contesto di riferimento: {materia}. 
Azione operativa richiesta in modo esclusivo: {task_operativo}. 
Regola fondamentale: Esegui unicamente l'azione selezionata, focalizzandoti solo sui KPI didattici o tecnici specifici del grado scolastico selezionato, senza preamboli o convenevoli. Restituisci un output rigoroso, pulito e formattato in Markdown."""

                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",  # Aggiornato al modello standard stabile supportato
                    system_instruction=system_instruction
                )
                
                response = model.generate_content(testo_utente)
                output_generato = response.text
                
                timestamp_attuale = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor = db_conn.cursor()
                cursor.execute(
                    "INSERT INTO storico (timestamp, materia, task, testo_origine, risultato) VALUES (?, ?, ?, ?, ?)",
                    (timestamp_attuale, materia, task_operativo, testo_utente, output_generato)
                )
                db_conn.commit()
                
                # Salvataggio in session state per rendere disponibile il tasto di download
                st.session_state['ultimo_output_universale'] = output_generato
                st.session_state['ultimo_task_universale'] = task_operativo
                
                st.success("Elaborazione completata e salvata nell'archivio universale!")

            except Exception as e:
                st.error(f"Errore durante l'elaborazione con le API di Gemini: {e}")

# --- VISUALIZZAZIONE RISULTATO E TASTO DOWNLOAD (PERSISTENTI IN SESSIONE) ---
if 'ultimo_output_universale' in st.session_state:
    st.markdown("---")
    st.subheader(f"Risultato per: {st.session_state.get('ultimo_task_universale', 'Elaborazione')}")
    st.markdown(st.session_state['ultimo_output_universale'])
    
    st.markdown("---")
    st.download_button(
        label="📥 Scarica il lavoro generato (File di Testo)",
        data=st.session_state['ultimo_output_universale'],
        file_name="risultato_agente_universale.txt",
        mime="text/plain"
    )

# --- SEZIONE ARCHIVIO STORICO (DATABASE PERSISTENTE) ---
st.markdown("---")
st.subheader("Archivio Universale (Storico Elaborazioni Salvate)")
if st.button("Visualizza Storico dal Database"):
    cursor = db_conn.cursor()
    cursor.execute("SELECT timestamp, materia, task, risultato FROM storico ORDER BY id DESC LIMIT 5")
    righe = cursor.fetchall()
    if not righe:
        st.info("L'archivio è attualmente vuoto.")
    else:
        for riga in righe:
            with st.expander(f"[{riga[0]}] {riga[1]} -> {riga[2]}"):
                st.markdown(riga[3])
