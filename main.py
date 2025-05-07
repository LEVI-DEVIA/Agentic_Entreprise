import asyncio
import os
import json
import re
from datetime import datetime

from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from langchain_openai import ChatOpenAI
from tools.generate_function import generer_mots_cles_seo

# Charger les variables d'environnement
load_dotenv()


async def main():
    # Vérification de la clé API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY n'est pas disponible")

    # Configuration du serveur MCP Playwright
    mcp_server_playwright = MCPServerStdio(
        command="npx",
        args=[
            "-y",
            "@smithery/cli@latest",
            "run",
            "@microsoft/playwright-mcp",
            "--key",
            "354a8c9a-46de-4ac1-bd88-6d845121ea09",
            "--headless=false",  # Mettre à true en production
        ],
    )

    # Configuration du modèle LLM
    """llm = ChatOpenAI(
        model="gpt-4o-mini",
        max_tokens=2000,  # Augmenté pour obtenir des réponses plus complètes
        temperature=0.2,
        api_key=SecretStr(api_key),
    )
"""
    # Génération des mots-clés SEO
    keywords = generer_mots_cles_seo(sujet="transformation de mangue")
    print(f"Mots-clés générés: {keywords}")

    # Structure pour stocker les données structurées
    companies_data = []

    # Initialisation de l'agent avec MCP
    agent = Agent(
        model="openai:gpt-4o-mini",
        mcp_servers=[mcp_server_playwright],
    )

    # Lancement des serveurs MCP
    async with agent.run_mcp_servers():
        print("Connexion au serveur Playwright établie...")

        # Recherche pour chaque mot-clé
        for keyword in keywords:
            print(f"\nRecherche en cours pour: {keyword}")

            # Prompt de recherche avec instructions détaillées
            prompt = f"""
            Tu es un assistant de recherche spécialisé dans l'industrie agroalimentaire en Côte d'Ivoire.
            
            TÂCHE: 
            1. Recherche sur Google le mot-clé: "{keyword}"
            2. Analyse les résultats pour identifier les entreprises de transformation de mangue en Côte d'Ivoire
            3. Pour chaque entreprise pertinente, visite son site web et collecte les informations suivantes:
               - Nom de l'entreprise
               - URL du site web
               - Localisation précise
               - Principales activités liées à la transformation de mangue
               - Année de création/fondation
               - Capacité de production
               - Nombre d'employés
               - Marchés d'exportation
               - Certifications obtenues
               - Produits dérivés de mangue
               - Chiffre d'affaires (si disponible)
               - Projets d'expansion
               - Contacts commerciaux
               - Avantages compétitifs
            
            INSTRUCTIONS SPÉCIALES:
            - Analyse au moins 3 sites web d'entreprises différentes
            - Assure-toi que les sites sont réellement liés à des entreprises de transformation de mangue
            - Vérifie que les liens sont fonctionnels avant de collecter les informations
            - Si une information n'est pas disponible, indique "Non disponible"
            
            FORMAT DE SORTIE:
            Fournir les données au format JSON structuré comme suit:
            ```json
            [
              {{
                "name": "Nom de l'entreprise",
                "url": "URL du site web",
                "location": "Localisation",
                "main_activity": "Activités principales",
                "founded": "Année de fondation",
                "production_capacity": "Capacité de production",
                "employees": "Nombre d'employés",
                "export_markets": "Marchés d'exportation",
                "certifications": "Certifications",
                "products": "Produits dérivés",
                "revenue": "Chiffre d'affaires",
                "expansion_plans": "Projets d'expansion",
                "contact": "Coordonnées",
                "competitive_advantages": "Avantages compétitifs"
              }}
            ]
            ```
            """

            try:
                # Exécution de la recherche avec Playwright
                result = await agent.run(
                    prompt,
                    tools=["playwright"],
                )
                result_text = result.output

                print(f"Résultat obtenu pour '{keyword}'")

                # Extraction des données JSON de la réponse
                json_match = re.search(r"```json\n([\s\S]*?)\n```", result_text)
                if json_match:
                    try:
                        json_data = json.loads(json_match.group(1))
                        if isinstance(json_data, list):
                            companies_data.extend(json_data)
                            print(f"Données extraites: {len(json_data)} entreprises")
                        else:
                            print("Format JSON invalide, attendu: liste d'objets")
                    except json.JSONDecodeError as e:
                        print(f"Erreur lors du parsing JSON: {e}")
                else:
                    print("Aucune donnée JSON trouvée dans la réponse")

            except Exception as e:
                print(f"Erreur lors de la recherche pour {keyword}: {e}")
                import traceback

                traceback.print_exc()

    # Dédupliquer les entreprises par nom (cas insensible)
    unique_companies = {}
    for company in companies_data:
        key = company.get("name", "").lower().strip()
        if key:
            # Si cette entreprise existe déjà, fusionner les informations
            if key in unique_companies:
                for field, value in company.items():
                    if value and (
                        field not in unique_companies[key]
                        or not unique_companies[key][field]
                    ):
                        unique_companies[key][field] = value
            else:
                unique_companies[key] = company

    # Reconvertir en liste
    companies_data = list(unique_companies.values())

    # Vérification des données avant écriture
    print(f"\nNombre total d'entreprises trouvées: {len(companies_data)}")
    if len(companies_data) > 0:
        print(f"Exemple de données: {companies_data[0]}")

    # Écriture des résultats formatés dans un fichier texte
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"entreprises_mangue_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("ENTREPRISES DE TRANSFORMATION DE MANGUE EN CÔTE D'IVOIRE\n")
        f.write("=====================================================\n")
        f.write(
            f"Date de recherche: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        )

        if not companies_data:
            f.write("Aucune entreprise trouvée.\n")
        else:
            for i, company in enumerate(companies_data, 1):
                f.write(f"Entreprise {i}: {company.get('name', 'Non disponible')}\n")
                f.write(
                    "".join(
                        [
                            "-"
                            for _ in range(
                                len(
                                    f"Entreprise {i}: {company.get('name', 'Non disponible')}"
                                )
                            )
                        ]
                    )
                    + "\n"
                )
                f.write(f"  URL: {company.get('url', 'Non disponible')}\n")
                f.write(
                    f"  Localisation: {company.get('location', 'Non disponible')}\n"
                )
                f.write(
                    f"  Principales activités: {company.get('main_activity', 'Non disponible')}\n"
                )

                # Ajout des champs détaillés
                f.write(
                    f"  Année de fondation: {company.get('founded', 'Non disponible')}\n"
                )
                f.write(
                    f"  Capacité de production: {company.get('production_capacity', 'Non disponible')}\n"
                )
                f.write(
                    f"  Nombre d'employés: {company.get('employees', 'Non disponible')}\n"
                )
                f.write(
                    f"  Marchés d'exportation: {company.get('export_markets', 'Non disponible')}\n"
                )
                f.write(
                    f"  Certifications: {company.get('certifications', 'Non disponible')}\n"
                )
                f.write(
                    f"  Produits dérivés: {company.get('products', 'Non disponible')}\n"
                )
                f.write(
                    f"  Chiffre d'affaires: {company.get('revenue', 'Non disponible')}\n"
                )
                f.write(
                    f"  Projets d'expansion: {company.get('expansion_plans', 'Non disponible')}\n"
                )
                f.write(f"  Contact: {company.get('contact', 'Non disponible')}\n")
                f.write(
                    f"  Avantages compétitifs: {company.get('competitive_advantages', 'Non disponible')}\n"
                )
                f.write("\n")

        # Ajouter une section pour les investisseurs
        f.write("\nRÉSUMÉ POUR INVESTISSEURS\n")
        f.write("=======================\n\n")
        f.write(
            "Ce rapport contient des informations sur les principales entreprises de transformation de mangue en Côte d'Ivoire.\n"
        )

        # Calculer quelques statistiques si possible
        if companies_data:
            # Calculer la capacité moyenne de production si disponible
            capacities = []
            for company in companies_data:
                cap = company.get("production_capacity", "")
                if cap and "Non disponible" not in cap:
                    # Essayer d'extraire un nombre
                    num_match = re.search(r"(\d+(?:\.\d+)?)", cap)
                    if num_match:
                        try:
                            capacities.append(float(num_match.group(1)))
                        except ValueError:
                            pass

            if capacities:
                avg_capacity = sum(capacities) / len(capacities)
                f.write(
                    f"Capacité moyenne de production: {avg_capacity:.1f} tonnes (basée sur {len(capacities)} entreprises)\n"
                )

            # Identifier les marchés d'exportation les plus courants
            all_markets = []
            for company in companies_data:
                markets = company.get("export_markets", "")
                if markets and "Non disponible" not in markets:
                    market_list = re.split(r",\s*", markets)
                    all_markets.extend([m.strip() for m in market_list if m.strip()])

            if all_markets:
                market_count = {}
                for market in all_markets:
                    market_count[market] = market_count.get(market, 0) + 1

                top_markets = sorted(
                    market_count.items(), key=lambda x: x[1], reverse=True
                )[:3]
                f.write("Principaux marchés d'exportation:\n")
                for market, count in top_markets:
                    f.write(f"  - {market}: mentionné par {count} entreprises\n")

            f.write("\n")
            f.write("OPPORTUNITÉS D'INVESTISSEMENT POTENTIELLES:\n")
            for company in companies_data:
                name = company.get("name", "Non disponible")

                # Ne mentionner que les entreprises avec des projets d'expansion
                expansion = company.get("expansion_plans", "")
                if expansion and "Non disponible" not in expansion:
                    f.write(f"  - {name}: {expansion}\n")

    # Écriture des données brutes en JSON pour analyse ultérieure
    json_filename = f"entreprises_mangue_{timestamp}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(companies_data, f, ensure_ascii=False, indent=2)

    print(f"\nFichier '{filename}' créé avec succès")
    print(f"Fichier JSON '{json_filename}' également créé")

    return f"Recherche terminée. Résultats enregistrés dans '{filename}' et '{json_filename}'."


if __name__ == "__main__":
    result = asyncio.run(main())
    print(result)
