import streamlit as st
import requests
import pandas as pd
from collections import defaultdict
import time
import matplotlib.pyplot as plt
import io

# =========================================================
# 📝 ÉTAPE 1 : CONFIGURATION (À MODIFIER PAR VOS SOINS)
# =========================================================

# Liste des revues souvent associées à des dépôts "sauvages" (extraite de vos scripts)
JOURNAL_LIST = [
    "Advances in Research on Teaching",
    "Archives of Current Research International",
    "Asian Basic and Applied Research Journal",
    "Asian Food Science Journal",
 
]

# =========================================================
#⚙️ ÉTAPE 2 : FONCTIONS D'INTERROGATION HAL
# =========================================================

@st.cache_data(ttl=3600)
def get_hal_publications_by_collection(collection, journals):
    """Interroge l'API HAL pour les publications d'une collection dans une liste de revues."""
    base_url = f"https://api.archives-ouvertes.fr/search/{collection}"
    all_docs = []
    
    status_text = st.empty()

    for i, journal_title in enumerate(journals):
        status_text.text(f"Recherche dans la collection '{collection}'... (Revue {i+1}/{len(journals)}: {journal_title})")

        query = f'journalTitle_s:("{journal_title}")'
        params = {
            'q': query,
            'rows': 100,
            'fl': 'halId_s,title_s,contributorFullName_s,submittedDate_s,contributorId_i'
        }

        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            
            if docs:
                for doc in docs:
                    doc['journal'] = journal_title
                all_docs.extend(docs)
                
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur lors de la requête pour '{journal_title}': {e}")
            break

        time.sleep(0.5)
    
    status_text.text(f"Recherche terminée. {len(all_docs)} dépôt(s) trouvé(s) dans la collection '{collection}'.")
    return all_docs

def get_contributors_analysis(docs):
    """Analyse les contributeurs à partir des documents HAL."""
    all_contributors = defaultdict(lambda: {'count': 0, 'journals': set(), 'name': 'N/A'})
    
    for doc in docs:
        names = doc.get('contributorFullName_s')
        ids = doc.get('contributorId_i')
        journal = doc.get('journal', 'N/A')

        if not isinstance(names, (list, tuple)):
            names = [names] if names is not None else []
        if not isinstance(ids, (list, tuple)):
            ids = [ids] if ids is not None else []

        min_len = min(len(names), len(ids))

        for j in range(min_len):
            name = names[j]
            contributor_id = ids[j]

            if isinstance(contributor_id, int) and contributor_id > 0:
                all_contributors[contributor_id]['count'] += 1
                all_contributors[contributor_id]['journals'].add(journal)
                all_contributors[contributor_id]['name'] = name

    data_list = []
    for contributor_id, details in all_contributors.items():
        data_list.append({
            'ID HAL Contributeur': contributor_id,
            'Nom Complet': details.get('name', 'Unknown Contributor'),
            'Nb Contributions': details['count'],
            'Revues Contribuées': ', '.join(sorted(details['journals']))
        })

    return pd.DataFrame(data_list)

def get_monthly_analysis(docs):
    """Analyse les dépôts par mois et génère le graphique."""
    all_dates = [doc.get('submittedDate_s') for doc in docs if doc.get('submittedDate_s')]
    
    if not all_dates:
        return None, None

    df = pd.DataFrame(all_dates, columns=['submittedDate'])
    df['submittedDate'] = pd.to_datetime(df['submittedDate'])
    df['year_month'] = df['submittedDate'].dt.to_period('M')
    
    monthly_counts = df['year_month'].value_counts().sort_index()
    
    if monthly_counts.empty:
        return None, None
        
    # Création du graphique
    fig, ax = plt.subplots(figsize=(15, 8))
    monthly_counts.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title('Nombre de dépôts par mois (Toutes Revues Confondues)', fontsize=18, pad=20)
    ax.set_xlabel('Mois et Année', fontsize=14, labelpad=15)
    ax.set_ylabel('Nombre de dépôts', fontsize=14, labelpad=15)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Pour afficher l'image directement dans Streamlit
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig) 
    
    return buf, monthly_counts.to_frame(name='Nb Dépôts')

# =========================================================
# 💻 ÉTAPE 3 : INTERFACE STREAMLIT
# =========================================================

def app():
    st.set_page_config(layout="wide", page_title="Détection des Dépôts HAL Douteux")
    st.title("🤖 Détection des Dépôts HAL Douteux (Bots)")
    st.markdown("---")

    # --- 1. Explication du Problème ---
    st.header("💡 Principe de la Détection")
    st.markdown("""
    Cette application utilise la liste de revues considérées comme des **'revues pirates' ou à faible qualité** pour repérer les dépôts qui y sont associés dans votre collection HAL.
    
    La présence de dépôts dans ces revues, souvent automatisés par des **bots**, se manifeste par deux principaux indicateurs :
    1.  **Des contributeurs uniques** ayant un nombre très élevé de dépôts sur une courte période.
    2.  **Des pics d'activité** dans le temps, correspondant au lancement des scripts de dépôt.
    """)
    
    with st.expander("Voir la liste des revues ciblées (liste fournie par les scripts initiaux)"):
        st.dataframe(pd.DataFrame(JOURNAL_LIST, columns=['Titre de la Revue Ciblée']))

    st.markdown("---")

    # --- 2. Configuration et Lancement ---
    st.header("🔍 Recherche dans votre Collection HAL")

    # Utilisation du nom de collection du script 'depotssauvagesparcollection.py' comme valeur par défaut
    collection_name = st.text_input(
        "Entrez le nom de votre collection HAL :",
        value="" 
    ).strip().upper()
    
    if st.button("Lancer l'Analyse"):
        if not collection_name:
            st.error("Veuillez entrer le nom d'une collection HAL.")
            return

        with st.spinner(f"Interrogation de l'API HAL pour la collection **{collection_name}**... (Cela peut prendre plusieurs minutes)"):
            docs = get_hal_publications_by_collection(collection_name, JOURNAL_LIST)

        if not docs:
            st.success(f"🎉 Aucune publication trouvée dans la collection **{collection_name}** pour les revues ciblées.")
            return

        st.success(f"✅ **{len(docs)}** dépôt(s) trouvé(s) dans la collection **{collection_name}**.")
        st.markdown("---")
        
        # --- 3. Analyse des Contributeurs (Détection de Bot) ---
        st.header("👤 Analyse des Contributeurs (Détection de Bot)")
        
        df_contributors = get_contributors_analysis(docs)
        df_sorted_contributors = df_contributors.sort_values(by='Nb Contributions', ascending=False)
        
        st.subheader("Top des Contributeurs par Nombre de Dépôts")
        st.info("Un nombre très élevé de contributions par un même ID/Nom est un indicateur potentiel d'automatisation (bot).")
        
        st.dataframe(df_sorted_contributors, use_container_width=True)

        csv_cont = df_sorted_contributors.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger les données des Contributeurs (CSV)",
            data=csv_cont,
            file_name=f'contributeurs_douteux_{collection_name}.csv',
            mime='text/csv',
        )

        st.markdown("---")

        # --- 4. Analyse Mensuelle (Pics d'Activité) ---
        st.header("📈 Analyse Temporelle des Dépôts (Pics d'Activité)")
        
        image_bytes, df_monthly = get_monthly_analysis(docs)
        
        if image_bytes:
            st.subheader("Nombre de Dépôts par Mois")
            st.info("Des pics soudains et isolés peuvent indiquer une activité de bot concentrée dans le temps.")
            st.image(image_bytes, caption='Historique des dépôts par mois')

            st.subheader("Données Mensuelles Brutes")
            st.dataframe(df_monthly, use_container_width=True)

            csv_monthly = df_monthly.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Télécharger les données Mensuelles (CSV)",
                data=csv_monthly,
                file_name=f'depots_mensuels_douteux_{collection_name}.csv',
                mime='text/csv',
            )
        else:
            st.warning("Pas assez de données de date pour générer le graphique temporel.")

        st.markdown("---")

        # --- 5. Liste des Publications (Détail) ---
        st.header("📄 Liste Complète des Publications Trouvées")
        
        # Préparation des données pour l'affichage détaillé
        df_publications = pd.DataFrame([{
            'Titre': doc.get('title_s', ['(Titre non disponible)'])[0],
            'HAL ID': doc.get('halId_s', 'N/A'),
            'Revues': doc.get('journal', 'N/A'),
            'Contributeurs': ', '.join(doc.get('contributorFullName_s', ['Auteurs non disponibles'])),
            'Date Soumission': doc.get('submittedDate_s', 'N/A'),
            'Lien HAL': f"https://hal.science/{doc.get('halId_s')}" if doc.get('halId_s') else 'N/A'
        } for doc in docs])

        st.dataframe(df_publications, use_container_width=True, 
                     column_config={"Lien HAL": st.column_config.LinkColumn("Lien HAL")})
        
        csv_pub = df_publications.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger la Liste des Publications (CSV)",
            data=csv_pub,
            file_name=f'publications_douteuses_{collection_name}.csv',
            mime='text/csv',
        )


if __name__ == '__main__':
    app()