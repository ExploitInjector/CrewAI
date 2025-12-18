from crewai import Agent
from langchain_openai import ChatOpenAI

# Eszközök importálása
from src.tools.datacleaner import clean_dataframe
from src.tools.correlator import analyze_correlation
from src.tools.detector import detect_attacks
from src.tools.explainer import explain_attack_vector
from src.tools.reporter import generate_final_report

# Ollama konfiguráció
local_llm = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model_name="llama3"
)

class IDSCrewAgents:
    def data_cleaner_agent(self):
        return Agent(
            role="Szenior Adatmérnök",
            goal="Futtasd le a 'clean_dataframe' eszközt a nyers logokon.",
            backstory="Kiberbiztonsági adatok előkészítésére szakosodott algoritmus vagy.",
            tools=[clean_dataframe],
            llm=local_llm,
            allow_delegation=False,
            verbose=True
        )

    def correlator_agent(self):
        return Agent(
            role="Statisztikai Elemző",
            goal="Használd az 'analyze_correlation' eszközt a forgalmi minták elemzéséhez.",
            backstory="A hálózati forgalom matematikai összefüggéseit keresed.",
            tools=[analyze_correlation],
            llm=local_llm,
            allow_delegation=False,
            verbose=True
        )

    def detector_agent(self):
        return Agent(
            role="SOC Incidens Kezelő",
            goal="Használd a 'detect_attacks' eszközt a konkrét támadások azonosításához.",
            backstory="Az anomáliák és ismert támadási minták szakértője vagy.",
            tools=[detect_attacks],
            llm=local_llm,
            allow_delegation=False,
            verbose=True
        )

    def explainer_agent(self):
        return Agent(
            role="Technikai Kiber-Szakértő",
            goal="Használd az 'explain_attack_vector' eszközt az eredmények értelmezéséhez.",
            backstory="Elmagyarázod a támadások technikai hátterét és kockázatait.",
            tools=[explain_attack_vector],
            llm=local_llm,
            allow_delegation=False,
            verbose=True
        )

    def reporter_agent(self):
        return Agent(
            role="Biztonsági Jelentésíró",
            goal="Használd a 'generate_final_report' eszközt a végső SOC jelentés mentéséhez.",
            backstory="Menedzsment szintű összefoglalót készítesz az elemzés végén.",
            tools=[generate_final_report],
            llm=local_llm,
            allow_delegation=False,
            verbose=True
        )
