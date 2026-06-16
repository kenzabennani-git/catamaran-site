from catamaran_loisir import CatamaranLoisir
from catamaran_site.catamaran_sportif import CatamaranSportif


# Création des flottes
flotte_loisir = []
flotte_sportif = []


# Demande du type à traiter
type_cat = input("Quel type de catamaran voulez-vous traiter ? (Loisir/Sportif) : ")


if type_cat == "Loisir":

    # Instanciation d’un Catamaran Loisir
    c1 = CatamaranLoisir(
        1, "OceanDream", "Loisir",
        10.5, 5.2, 3.1,
        1.2, 20, 12, "B",
        "Voile standard", "Coque renforcée"
    )

    # Ajout à la flotte
    flotte_loisir.append(c1)

    # Appel des méthodes
    c1.afficherCaracteristiqueCatamaran_loisir()


elif type_cat == "Sportif":

    # Instanciation d’un Catamaran Sportif
    c2 = CatamaranSportif(
        2, "SpeedWave", "Sportif",
        8.0, 4.0, 2.5,
        1.0, 30, 6, "B",
        "Foc compétition", "Dérives carbone", "Grande voile racing"
    )

    # Ajout à la flotte
    flotte_sportif.append(c2)

    # Appel des méthodes
    c2.afficherCaracteristiqueCatamaran_sportif()


else:
    print("Type de catamaran inconnu.")