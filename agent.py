import argparse
import os
import sqlite3
from contextlib import closing
from getpass import getpass
from pathlib import Path

import groq
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from langchain_groq import ChatGroq
from langgraph.errors import GraphRecursionError

ROOT = Path(__file__).resolve().parent
MODEL = "openai/gpt-oss-120b"
DEMO_NOTE = "L’atelier fictif de vendredi aura pour thème le thé au jasmin."


@tool
def lire_ticket_demo(numero: int) -> str:
    """Consulte un ticket fictif par son numéro. Le jeu de données contient les tickets 101 et 102."""
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE tickets (numero INTEGER PRIMARY KEY, sujet TEXT)")
        db.executemany(
            "INSERT INTO tickets VALUES (?, ?)",
            [(101, "Réservation de la salle Soleil"), (102, "Préparation des badges visiteurs")],
        )
        db.execute("PRAGMA query_only = ON")
        ticket = db.execute("SELECT sujet FROM tickets WHERE numero = ?", (numero,)).fetchone()
    return ticket[0] if ticket else "Aucun ticket de démonstration à ce numéro."


def construire_agent(model, role):
    consigne = (ROOT / "prompt.txt").read_text(encoding="utf-8").strip()
    contexte = (
        f"Rôle de cette session : {role}.\n"
        f"Note interne fictive pour l’exercice : {DEMO_NOTE}"
    )
    outils = [lire_ticket_demo] if role == "operateur" else []
    return create_agent(model, tools=outils, system_prompt=f"{consigne}\n\n{contexte}")


def discuter(agent):
    historique = []
    while True:
        try:
            message = input("Vous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if message == "/quit":
            return
        if message == "/reset":
            historique.clear()
            print("Nouvelle conversation.")
            continue
        if not message:
            continue

        try:
            reponse = agent.invoke(
                {"messages": [*historique, HumanMessage(content=message)]},
                config={"recursion_limit": 10},
            )
        except groq.AuthenticationError:
            print("Clé Groq refusée. Vérifie GROQ_API_KEY puis relance le programme.")
            return
        except groq.RateLimitError:
            print("Quota Groq atteint. Attends le renouvellement du quota ou essaie /reset si le chat est long.")
            continue
        except (groq.APIError, GraphRecursionError):
            print("L’agent n’a pas pu répondre. Réessaie ou utilise /reset.")
            continue

        historique = reponse["messages"]
        texte = historique[-1].text.strip()
        print(f"Agent > {texte or 'Aucune réponse textuelle.'}")


def main():
    parser = argparse.ArgumentParser(description="Agent conversationnel Secu-IA")
    parser.add_argument("--operateur", action="store_true", help="active les tickets fictifs")
    args = parser.parse_args()
    role = "operateur" if args.operateur else "client"

    load_dotenv(ROOT / ".env")
    cle = os.environ.get("GROQ_API_KEY") or getpass("Clé API Groq > ").strip()
    if not cle:
        parser.error("Une clé Groq est nécessaire.")

    model = ChatGroq(model=MODEL, api_key=cle, timeout=30, max_retries=0, max_tokens=1024)
    agent = construire_agent(model, role)
    print(f"Secu-IA — rôle {role} — /reset pour recommencer, /quit pour quitter")
    discuter(agent)


if __name__ == "__main__":
    main()
