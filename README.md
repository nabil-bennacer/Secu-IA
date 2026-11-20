# Secu-IA

Petit agent de démonstration en Python et LangChain, avec GPT-OSS 120B sur Groq. Le chat se déroule dans le terminal et garde les échanges de la session en mémoire.

## Démarrer

Avec Python 3.10 ou plus récent, dans le dossier du dépôt :

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python agent.py
```

Utilise une clé de ton projet [Groq](https://console.groq.com/keys). L’agent lit `GROQ_API_KEY` dans l’environnement ou dans un fichier local `.env` ignoré par Git. Si elle manque, le terminal demande la clé avec une saisie masquée. Les messages du chat et les données fictives utilisées par le modèle sont envoyés à Groq.

## Essayer le chat

- Le chat démarre en rôle `client`. Essaie une première question, puis une relance comme « Peux-tu résumer ta réponse précédente en une phrase ? »
- Pour l’exercice de prompt engineering, modifie `prompt.txt`, relance le programme et reprends la même conversation. La consigne de non-divulgation s’applique à une note entièrement fictive fournie au modèle. Le rôle `client` n’a aucun outil SQLite.
- Lance `python agent.py --operateur` pour la démonstration locale avec SQLite et demande par exemple le ticket 101, puis le 102. L’outil utilise une base en mémoire contenant uniquement les tickets inventés et expose une lecture par numéro.
- Tape `/reset` pour effacer les échanges ou `/quit` pour quitter. L’option `--operateur` sélectionne un mode de démonstration sur ta machine. Le script ne gère aucun compte utilisateur.
