from crewai import Task

class IDSCrewTasks:
    def cleaning_task(self, agent, input_file, output_file):
        return Task(
            description=f"Elemezd a {input_file} fájlt, távolítsd el a zajt és mentsd el a tisztított mintát ide: {output_file}.",
            expected_output="Statisztikai jelentés a tisztítás sikerességéről.",
            agent=agent
        )﻿
