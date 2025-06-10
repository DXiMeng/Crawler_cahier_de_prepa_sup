import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import argparse
import getpass  # pour cacher le mot de passe



base_url = "https://cahier-de-prepa.fr/mp2i-saintlouis/"
main_url = urljoin(base_url, "docs?maths")

def sanitize(name):
    return "".join(c for c in name if c.isalnum() or c in " _-").strip()

def download_files(session, url, path, update=False):
    r = session.get(url)
    if r.status_code != 200:
        print(f"❌ Échec d'accès à {url}")
        return

    page = BeautifulSoup(r.content, 'html.parser')
    section = page.find("section")
    if not section:
        print(f"❌ Section introuvable dans {url}")
        return

    # Coupe après <h3>Documents récents
    end = section.find("h3", string="Documents récents")
    if end:
        for tag in list(end.find_all_next()):
            tag.decompose()
        end.decompose()

    # Crée le dossier si nécessaire
    os.makedirs(path, exist_ok=True)

    # 🔁 Parcours des répertoires
    for rep in section.find_all("p", class_="rep"):
        nom_rep = rep.find("span", class_="nom")
        a_tag = rep.find("a")
        if nom_rep and a_tag:
            nom_dossier = sanitize(nom_rep.text)
            href = a_tag['href']
            next_url = urljoin(url, href)
            next_path = os.path.join(path, nom_dossier)
            download_files(session, next_url, next_path, update=update)

    # 📥 Téléchargement des PDF
    for doc in section.find_all("p", class_="doc"):
        nom_doc = doc.find("span", class_="nom")
        a_tag = doc.find("a")
        if nom_doc and a_tag:
            href = a_tag['href']
            nom_fichier = sanitize(nom_doc.text) + ".pdf"
            fichier_path = os.path.join(path, nom_fichier)
            download_url = urljoin(base_url, href)

            if os.path.exists(fichier_path) and update:
                print(f"⏭️  Déjà présent : {nom_fichier}")
                continue  # passe au fichier suivant

            print(f"📥 Téléchargement de {nom_fichier}")
            file_response = session.get(download_url)
            if file_response.status_code == 200:
                with open(fichier_path, 'wb') as f:
                    f.write(file_response.content)
                    print(f"✅ Téléchargé : {nom_fichier}")
            else:
                print(f"❌ Erreur téléchargement : {download_url}")


def main():
    parser = argparse.ArgumentParser(description="Télécharge les documents du site Cahier de Prépa.")

    parser.add_argument('--update', action='store_true', help="Ne télécharge que les fichiers nouveaux (ignore ceux déjà présents).")
    parser.add_argument('--login', type=str, help="Identifiant de connexion.")
    parser.add_argument('--password', type=str, help="Mot de passe de connexion.")
    args = parser.parse_args()

    session = requests.Session()
    if not args.login:
        args.login = input("Identifiant : ")
    if not args.password:
        args.password = getpass.getpass("Mot de passe : ")
    if not args.update:
        args.update = input("Mettre à jour uniquement les nouveaux fichiers ? (N/Y) ").strip().lower() == 'y'

    payload = {
        'login': args.login,
        'motdepasse': args.password
    }

    # 🔐 Connexion unique
    login_url = main_url
    login_response = session.post(login_url, data=payload)
    if login_response.status_code != 200:
        print("❌ Échec de connexion")
        return

    # ✅ Lancement du téléchargement
    racine = "cahier-de-prepa"
    os.makedirs(racine, exist_ok=True)
    download_files(session, main_url, racine, update=args.update)

if __name__ == "__main__":
    main()
