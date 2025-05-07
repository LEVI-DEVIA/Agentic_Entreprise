from dotenv import load_dotenv
import os
import re
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generer_mots_cles_seo(sujet: str, n_mots: int = 20) -> list:
    """
    Génère une liste de mots-clés SEO pour le sujet donné.

    Args:
        sujet: Le sujet pour lequel générer des mots-clés
        n_mots: Nombre de mots-clés à générer (par défaut 20)

    Returns:
        Une liste de mots-clés
    """
    prompt = f"""
Génère une liste précise et optimisée de mots-clés SEO à partir du sujet suivant : "{sujet}" en Côte d'Ivoire. 
Objectif : identifier facilement des entreprises, organisations, ou opportunités d'affaires en lien avec ce sujet en Côte d'Ivoire. 
Inclure :
- Des mots-clés généraux en rapport avec le sujet
- Des types de produits, services ou technologies associés à ce domaine
- Des termes liés à l'investissement ou à la recherche d'opportunités économiques
- Des mots-clés liés au commerce, à l'exportation ou à l'industrie locale
- Des localisations stratégiques (villes, zones industrielles, régions agricoles)
- Des mots-clés relatifs aux acteurs du secteur : fédérations, groupements, coopératives ou entreprises connues
Contraintes :
- Génère exactement {n_mots} mots-clés
- Chaque mot-clé doit contenir **au moins 2 mots**
- Les mots-clés doivent être fournis en **français**
- Formate-les en une liste numérotée simple avec le format "1. mot-clé", "2. mot-clé", etc.
- PAS d'introduction ni d'explication, uniquement la liste numérotée
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,  # Pour plus de précision dans les recherches
    )

    result = response.choices[0].message.content

    pattern = r"(\d+)\.\s+(.*?)(?=\n\d+\.|\n*$)"
    matches = re.findall(pattern, result, re.DOTALL)

    mots_cles = [mot_cle.strip() for _, mot_cle in matches]

    return mots_cles


"""
if __name__ == "__main__":
    mots = generer_mots_cles_seo("transformation de mangue")
    for i, mot in enumerate(mots, 1):
        print(f"{i}. {mot}")"""
