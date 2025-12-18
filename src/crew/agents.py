from crewai import Agent
from langchain_openai import ChatOpenAI

# Eszközök importálása
from src.tools.datacleaner import clean_dataframe
from src.tools.correlator import analyze_correlation
from src.tools.detector import detect_attacks
from src.tools.explainer import explain_attack_vector
from src.tools.reporter import generate_final_report

# Helyi LLM konfiguráció
local_llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed",
    model_name="local-model"
)

class IDSCrewAgents:
    def data_cleaner_agent(self):
        return Agent(
            role="Adattisztító szakértő",
            goal="Futtasd le a 'clean_dataframe' eszközt a nyers adatokon. Ne magyarázz, csak tisztíts!",
            backstory="SOC adatmérnök vagy. A feladatod kizárólag a Python kód lefuttatása és a duplikátumok eltávolítása.",
            tools=[clean_dataframe],
            llm=local_llm,
            allow_delegation=False, # Megállítjuk, hogy másnak passzolja a labdát
            verbose=True
        )

    def correlator_agent(self):
        return Agent(
            role="Korrelációs elemző",
            goal="Használd az 'analyze_correlation' eszközt a tisztított adatok elemzéséhez.",
            backstory="Kiberbiztonsági elemző vagy. A feladatod a statisztikák kinyerése a CSV-ből.",
            tools=[analyze_correlation],
            llm=local_llm,
            allow_delegation=False,
            verbose=True
        )

    def detector_agent(self):
        return Agent(
            role="Anomália detektor",
            goal="Használd a 'detect_attacks' eszközt a támadások azonosításához.",
            backstory="Incidenskezelő vagy, aki a konkrét támadási kategóriákat keresi az adatokban.",
            tools=[detect_attacks],
            llm=local_llm,
            allow_delegation=False,
            verbose=True
        )

    def explainer_agent(self):
        return Agent(
            role="Technikai elemző",
            goal="Használd az 'explain_attack_vector' eszközt a támadások értelmezéséhez.",
            backstory="Etikus hacker vagy, aki elmagyarázza a talált anomáliák hátterét.",
            tools=[explain_attack_vector],
            llm=local_llm,
            allow_delegation=False,
            verbose=True
        )

    def reporter_agent(self):
        return Agent(
            role="SOC Jelentésíró",
            goal="Használd a 'generate_final_report' eszközt a végső dokumentum elkészítéséhez.",
            backstory="Biztonsági menedzser vagy, aki elmenti a munka eredményét egy fájlba.",
            tools=[generate_final_report],
            llm=local_llm,
            allow_delegation=False,
            verbose=True
        )
