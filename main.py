from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser
from dotenv import load_dotenv
from pydantic import SecretStr

import asyncio
import os
import json
import re
from datetime import datetime


load_dotenv()

# Chargement de la clé API OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY n'est pas disponible")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=SecretStr(api_key),
)

keyWords = [
    "séchage mangue Côte d'Ivoire",
    "groupement transformateurs mangue",
]


# Prompt amélioré avec des instructions plus précises
prompt = f"""
Tu es un assistant de recherche spécialisé dans l'industrie agroalimentaire en Côte d'Ivoire.

TÂCHE: Identifie les principales entreprises de transformation de mangue en Côte d'Ivoire à partir des recherches des mot-clé: {keyWords}.

Pour chaque entreprise, extrait UNIQUEMENT les informations suivantes:
1. Nom de l'entreprise
2. URL de son site web
3. Localisation
4. Principales activités liées à la transformation de mangue

FORMAT DE SORTIE:
Présente les résultats sous forme d'une liste structurée avec ces 4 informations pour chaque entreprises.
Si une information n'est pas disponible, indique-le clairement par "Non disponible".

Ne fournit pas d'informations supplémentaires ni d'analyses. Concentre-toi uniquement sur l'extraction et la présentation des 4 éléments demandés pour chaque entreprises.
"""


async def main():
    # Création de structures pour stocker les données structurées
    all_results_raw = []
    companies_data = []

    # Recherche pour chaque mot-clé
    for keyword in keyWords:
        print(f"Recherche en cours pour: {keyword}")
        search_prompt = f"{prompt}\n\n"

        agent = Agent(
            task=search_prompt,
            use_vision=False,
            llm=llm,
        )
        result = await agent.run()
        await Browser.close()
        all_results_raw.append(f"--- Résultats pour '{keyword}' ---\n{result}\n\n")
    # Tenter d'extraire les structures JSON du résultat

    return f"Les Resultats : {all_results_raw}"


if __name__ == "__main__":
    asyncio.run(main())
