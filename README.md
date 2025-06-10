# Crawler_cahier_de_prepa_sup
Un crawler pour télécharger tous les documents de cahier de prépa. Conçu pour celui de MP2I à Saint-Louis. 

Pour utiliser : 
- téléchargez le script python
- les libraries utilisées sont : os, requests, bs4, urllib.parse, argparse, getpass
- glissez le script dans le dossier target (par exemple Desktop)
- python3 crawler.py --login "[identifiant]" --password "[mdp_cdp]" --update (pour ne télécharger que les fichiers manquant dans le dossier cahier-de-prepa)
- OU python3 crawler.py (puis saisir les entrées)
