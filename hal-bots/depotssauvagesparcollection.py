# =========================================================
# 📝 ÉTAPE 1 : INSTALLATION DES BIBLIOTHÈQUES
# =========================================================
# Cette ligne installe la bibliothèque 'requests' nécessaire.
# Elle est exécutée au début, une seule fois.
%pip install requests

# =========================================================
# 📝 ÉTAPE 2 : CONFIGURATION (À MODIFIER PAR VOS SOINS)
# =========================================================
# ➡️ Entrez le nom de votre collection HAL

hal_collection = "MIP"

# ➡️ Entrez la liste des revues que vous souhaitez interroger
#    Chaque titre de revue doit être entre guillemets et séparé par une virgule.
journal_list = [
    "Advances in Research on Teaching",
    "Archives of Current Research International",
    "Asian Basic and Applied Research Journal",
    "Asian Food Science Journal",
    "Asian Journal of Advanced Research and Reports",
    "Asian Journal of Advances in Agricultural Research",
    "Asian Journal of Advances in Research",
    "Asian Journal of Agricultural and Horticultural Research",
    "Asian Journal of Agricultural Extension, Economics and Sociology",
    "Asian Journal of Arts, Humanities and Social Studies",
    "Asian Journal of Biochemistry, Genetics and Molecular Biology",
    "Asian Journal of Biology",
    "Asian Journal of Cardiology Research",
    "Asian Journal of Case Reports in Medicine and Health",
    "Asian journal of case reports in surgery",
    "Asian Journal of Chemical Sciences",
    "Asian Journal of Current Research",
    "Asian Journal of Dental Sciences",
    "Asian Journal of Economics, Business and Accounting",
    "Asian Journal of Economics, Finance and Management",
    "Asian Journal of Education and Social Studies",
    "Asian Journal of Fisheries and Aquatic Research",
    "Asian Journal of Food Research and Nutrition",
    "Asian Journal of Language, Literature and Culture Studies",
    "Asian Journal of Medicine and Health",
    "Asian Journal of Microbiology, Biotechnology and Environmental Sciences",
    "Asian Journal of Orthopaedic Research",
    "Asian Journal of Pediatric Research",
    "Asian Journal of Plant and Soil Sciences",
    "Asian Journal of Research and Reports in Endocrinology",
    "Asian Journal of Research and Reviews in Physics",
    "Asian Journal of Research in Agriculture and Forestry",
    "Asian Journal of Research in Biochemistry",
    "Asian Journal of Research in Botany",
    "Asian Journal of Research in Computer Science",
    "Asian Journal of Research in Crop Science",
    "Asian Journal of Research in Dermatological Science",
    "Asian Journal of Research in Infectious Diseases",
    "Asian Journal of Research in Medicine and Medical Science",
    "Asian Journal of Research in Nephrology",
    "Asian Journal of Research in Nursing and Health",
    "Asian Journal of Research in Surgery",
    "Asian Journal of Research in Zoology",
    "Asian Journal of Sociological Research",
    "Asian Journal of Soil Science and Plant Nutrition",
    "Asian Research Journal of Agriculture",
    "Asian Research Journal of Arts & Social Sciences",
    "Asian Research Journal of Mathematics",
    "Cardiology and Angiology: An International Journal",
    "Chemical Science International Journal",
    "Current Journal of Applied Science and Technology",
    "European Journal of Nutrition and Food Safety",
    "International Journal of Advances in Nephrology Research",
    "International Journal of Biochemistry Research & Review",
    "International Journal of Environment and Climate Change",
    "International Journal of Hematology-Oncology and Stem Cell Research",
    "International Journal of Medical and Pharmaceutical Case Reports",
    "International Journal of Pathogen Research",
    "International Journal of Plant & Soil Science",
    "international journal of research and reports in dentistry",
    "International Journal of Research and Reports in Hematology",
    "International Neuropsychiatric Disease Journal",
    "International Research Journal of Gastroenterology and Hepatology",
    "International Research Journal of Oncology",
    "International Research Journal of Pure and Applied Chemistry",
    "Journal of Advances in Biology & Biotechnology",
    "Journal of Advances in Food Science & Technology",
    "Journal of Advances in Mathematics and Computer Science ",
    "Journal of Advances in Medicine and Medical Research",
    "Journal of Advances in Microbiology",
    "Journal of Agriculture and Ecology Research International",
    "Journal of Applied Chemical Science International",
    "Journal of Applied Life Sciences International",
    "Journal of Biochemistry International",
    "Journal of Biology and Nature",
    "Journal of Case Reports in Medical Science",
    "Journal of Complementary and Alternative Medical Research",
    "Journal of Economics and Trade",
    "Journal of Economics, Management and Trade",
    "Journal of Education, Society and Behavioural Science",
    "Journal of Engineering Research and Reports",
    "Journal of Experimental Agriculture International",
    "Journal of Geography, Environment and Earth Science International",
    "Journal of Global Ecology and Environment",
    "Journal of Materials Science Research and Reviews",
    "Journal of Pharmaceutical Research International",
    "Journal of Scientific Research and Reports",
    "Ophthalmology Research: An International Journal",
    "Physical Science International Journal",
    "Plant Cell Biotechnology and Molecular Biology",
    "South Asian Journal of Research in Microbiology",
    "South Asian Journal of Social Studies and Economics",
    "UTTAR PRADESH JOURNAL OF ZOOLOGY"
]

# =========================================================
# ⚙️ ÉTAPE 3 : EXÉCUTION DU SCRIPT (NE PAS MODIFIER)
# =========================================================
# Le code des fonctions est placé ici, pour qu'il soit défini avant d'être appelé.
import requests
import time

def get_hal_publications(collection, journals):
    """
    Interroge l'API HAL pour trouver les publications d'une collection
    spécifique pour une liste de revues, en utilisant le point d'entrée
    de l'instance de collection pour une meilleure fiabilité.
    """
    base_url = f"https://api.archives-ouvertes.fr/search/{collection}"
    results = {}

    print(f"Lancement de la recherche de publications dans la collection '{collection}'...")

    for journal_title in journals:
        print(f"\nRecherche pour la revue : '{journal_title}'...")

        query = f'journalTitle_s:("{journal_title}")'
        params = {
            'q': query,
            'rows': 100,
            'fl': 'halId_s,title_s,contributorFullName_s,submittedDate_s'
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            docs = data.get('response', {}).get('docs', [])

            if docs:
                results[journal_title] = docs
                print(f"  -> ✅ {len(docs)} publication(s) trouvée(s).")
            else:
                print(f"  -> ❌ Aucune publication trouvée pour cette revue dans la collection.")
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête pour '{journal_title}': {e}")

        time.sleep(0.5)

    return results

def display_results(publications):
    """
    Affiche les résultats de la recherche de manière lisible.
    """
    if not publications:
        print("Aucune publication trouvée pour les critères spécifiés.")
        return

    for journal, docs in publications.items():
        print("\n" + "="*80)
        print(f"  ▶️ PUBLICATIONS TROUVÉES DANS LA REVUE '{journal}'")
        print("="*80)

        for i, doc in enumerate(docs):
            title = doc.get('title_s', ['(Titre non disponible)'])[0]
            hal_id = doc.get('halId_s', None)
            uri = f"https://hal.science/{hal_id}" if hal_id else "(Lien non disponible)"

            contributors = doc.get('contributorFullName_s', ['Auteurs non disponibles'])
            if isinstance(contributors, str):
                contributors = [contributors]
            authors = ', '.join(contributors)

            print(f"  {i+1}. Titre : {title}")
            print(f"     Contributeur : {authors}")
            print(f"     Lien HAL : {uri}")
            print("-" * 70)

# Exécution du script principal
extracted_publications = get_hal_publications(hal_collection, journal_list)
display_results(extracted_publications)

print("\nFin de l'exécution.")