import requests
import pandas as pd
from collections import defaultdict
import time
import matplotlib.pyplot as plt

def get_deposit_dates_from_hal(journal_title):
    """
    Récupère les dates de soumission pour une revue donnée de l'API HAL.
    """
    base_url = "https://api.archives-ouvertes.fr/search"
    params = {
        'q': f'journalTitle_s:"{journal_title}"',
        'rows': 10000,
        'fl': 'submittedDate_s'
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        # Retourne une liste de dates de soumission
        return [doc.get('submittedDate_s') for doc in data.get('response', {}).get('docs', [])]
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête pour '{journal_title}': {e}")
        return []

def main():
    """
    Script principal pour analyser et visualiser les dépôts par mois.
    """
    # Votre liste de revues
    journals = [
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
        "International Research Journal of Gastroenterology and  Hepatology",
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

    all_dates = []
    
    print("Début de l'extraction des dates de dépôt de l'API HAL...")

    for i, journal in enumerate(journals):
        print(f"  [{i+1}/{len(journals)}] Récupération des dates pour '{journal}'...")
        dates = get_deposit_dates_from_hal(journal)
        all_dates.extend(dates)
        time.sleep(1) 

    # Conversion en DataFrame et traitement des données
    df = pd.DataFrame(all_dates, columns=['submittedDate'])
    df.dropna(inplace=True)
    
    # Conversion en datetime et extraction du mois et de l'année
    df['submittedDate'] = pd.to_datetime(df['submittedDate'])
    df['year_month'] = df['submittedDate'].dt.to_period('M')
    
    # Comptage des dépôts par mois
    monthly_counts = df['year_month'].value_counts().sort_index()
    
    if monthly_counts.empty:
        print("\n❌ Aucune donnée de dépôt n'a pu être extraite pour générer le graphique.")
        return
        
    print("\n✅ Données compilées. Création du graphique...")

    # Visualisation des données
    plt.figure(figsize=(15, 8))
    monthly_counts.plot(kind='bar', color='skyblue')
    plt.title('Nombre de dépôts par mois', fontsize=18, pad=20)
    plt.xlabel('Mois et année', fontsize=14, labelpad=15)
    plt.ylabel('Nombre de dépôts', fontsize=14, labelpad=15)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Sauvegarde du graphique en image
    output_filename = 'depots_par_mois.png'
    plt.savefig(output_filename)
    print(f"\n✅ Graphique sauvegardé sous le nom '{output_filename}'.")
    plt.show()

if __name__ == "__main__":
    main()