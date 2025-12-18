from crewai import Task

class IDSCrewTasks:
    def cleaning_task(self, agent):
        return Task(description="1. LÉPÉS: Adatok tisztítása.", expected_output="Tisztított CSV.", agent=agent)

    def correlation_task(self, agent, context):
        return Task(description="2. LÉPÉS: Összefüggések keresése.", expected_output="Korrelált adatok.", agent=agent, context=[context])

    def detection_task(self, agent, context):
        return Task(description="3. LÉPÉS: Támadások detektálása.", expected_output="Incidens lista.", agent=agent, context=[context])

    def explanation_task(self, agent, context):
        return Task(description="4. LÉPÉS: Eredmények magyarázata.", expected_output="Szöveges elemzés.", agent=agent, context=[context])

    def reporting_task(self, agent, context):
        return Task(description="5. LÉPÉS: Riort generálás.", expected_output="Záró dokumentum.", agent=agent, context=[context])
