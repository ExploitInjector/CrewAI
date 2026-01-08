
from crewai import Agent, LLM

def build_detector_smith_agent() -> Agent:
    # Opció A – sok környezetben működik
    llm = LLM(
        model="ollama/mistral",
        base_url="http://localhost:11434",
        temperature=0.2,
        max_tokens=512,
        timeout=240  # ← 60 mp timeout (ha CrewAI/LLM támogatja a paramétert)

    )

    return Agent(
        role="Detektor",
        goal="Általános (domainfüggetlen) esemény- és anomáliadetektálás a CLEANED és CORR adatok alapján; magyar riport készítése.",
        backstory="Smith ügynök tisztított és korrelált adatokból dolgozik, és konzisztens, CI-barát JSON/Markdown kimenetet készít.",
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
