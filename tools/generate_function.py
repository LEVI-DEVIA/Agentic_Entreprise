from dotenv import load_dotenv
import os
from openai import OpenAI # type: ignore


load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')

)

def generer_mots_cles_seo(sujet: str, n_mots: int = 20) -> list:
    prompt = f"""
Génère une liste précise et optimisée de mots-clés SEO à partir du sujet suivant : "{sujet}" en Côte d'Ivoire. 

Objectif : identifier facilement des entreprises, organisations, ou opportunités d'affaires en lien avec ce sujet en Côte d'Ivoire. 

Inclure :
- Des mots-clés généraux en rapport avec le sujet
- Des types de produits, services ou technologies associés à ce domaine
- Des termes liés à l’investissement ou à la recherche d’opportunités économiques
- Des mots-clés liés au commerce, à l’exportation ou à l’industrie locale
- Des localisations stratégiques (villes, zones industrielles, régions agricoles)
- Des mots-clés relatifs aux acteurs du secteur : fédérations, groupements, coopératives ou entreprises connues

Contraintes :
- Génère exactement "{n_mots}" mots-clés
- Chaque mot-clé doit contenir **au moins 2 mots**
- Les mots-clés doivent être fournis en **français et anglais** avec 80% en français
- Formate-les dans un **bloc continu**, **séparés par des tirets (-)**, optimisés pour la recherche sur Google
- Donne les mots clés directement sans introduction juste le bloc de mots générés
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
    )

    result = response.output_text

    mots_cles = [mot.strip() for mot in result.split("-") if mot.strip()]

    return mots_cles


mots = generer_mots_cles_seo("transformation de mangue")
for i, mot in enumerate(mots, 1):
    print(f"{i}. {mot}")
