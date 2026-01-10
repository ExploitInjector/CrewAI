from crewai import Task

class IDSCrewTasks:
    def cleaning_task(self, agent):
        return Task(
            description="Olvasd be a data/raw/csv/data.csv fájlt és végezz teljes adattisztítást.",
            expected_output="Egy tisztított és szabványosított CSV fájl a processed mappában.",
            agent=agent
        )

    def correlation_task(self, agent, context):
        return Task(
            description="Elemezd a tisztított adatokat: keress gyanús IP címeket és portokat.",
            expected_output="Statisztikai összefoglaló a hálózati forgalomról.",
            agent=agent,
            context=[context]
        )

    def detection_task(self, agent, context):
        return Task(
            description="Azonosítsd a konkrét támadási kísérleteket az adatokban.",
            expected_output="A detektált incidensek listája és súlyossága.",
            agent=agent,
            context=[context]
        )

    def explanation_task(self, agent, context):
        return Task(
            description="Értelmezd a talált támadásokat: mi történt pontosan a hálózaton?",
            expected_output="Részletes technikai leírás a támadási vektorokról.",
            agent=agent,
            context=[context]
        )

    def reporting_task(self, agent, context):
        return Task(
            description="Generáld le a végső jelentést PDF-be vagy Markdown-ba.",
            expected_output="A jelentés sikeres mentése és a folyamat lezárása.",
            agent=agent,
            context=[context]
        )
