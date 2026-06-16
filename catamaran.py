import random


class Catamaran:
    def __init__(
        self,
        id_catamaran,
        nom,
        type_catamaran,
        longueur,
        largeur,
        hauteur,
        tirant_eau,
        vitesse_noeud,
        capacite,
        categorie_type_B
    ):
        self.id_catamaran = id_catamaran
        self.nom = nom
        self.type_catamaran = type_catamaran
        self.longueur = longueur
        self.largeur = largeur
        self.hauteur = hauteur
        self.tirant_eau = tirant_eau
        self.vitesse_noeud = vitesse_noeud
        self.capacite = capacite
        self.categorie_type_B = categorie_type_B

    # Getters
    def get_id_catamaran(self):
        return self.id_catamaran

    def get_nom(self):
        return self.nom

    def get_type_catamaran(self):
        return self.type_catamaran

    def get_longueur(self):
        return self.longueur

    def get_largeur(self):
        return self.largeur

    def get_hauteur(self):
        return self.hauteur

    def get_tirant_eau(self):
        return self.tirant_eau

    def get_vitesse_noeud(self):
        return self.vitesse_noeud

    def get_capacite(self):
        return self.capacite

    def get_categorie_type_B(self):
        return self.categorie_type_B

    # Setters
    def set_nom(self, nom):
        self.nom = nom

    def set_type_catamaran(self, type_catamaran):
        self.type_catamaran = type_catamaran

    def set_longueur(self, longueur):
        self.longueur = longueur

    def set_largeur(self, largeur):
        self.largeur = largeur

    def set_hauteur(self, hauteur):
        self.hauteur = hauteur

    def set_tirant_eau(self, tirant_eau):
        self.tirant_eau = tirant_eau

    def set_vitesse_noeud(self, vitesse_noeud):
        self.vitesse_noeud = vitesse_noeud

    def set_capacite(self, capacite):
        self.capacite = capacite

    def set_categorie_type_B(self, categorie_type_B):
        self.categorie_type_B = categorie_type_B

    def afficheCaracteristiquesCatamaran(self, type_demande=None):
        if type_demande is None or self.type_catamaran == type_demande:
            return {
                "id": self.id_catamaran,
                "nom": self.nom,
                "type": self.type_catamaran,
                "longueur": self.longueur,
                "largeur": self.largeur,
                "hauteur": self.hauteur,
                "tirant_eau": self.tirant_eau,
                "vitesse_noeud": self.vitesse_noeud,
                "capacite": self.capacite,
                "categorie_type_B": self.categorie_type_B
            }
        return None

    def afficheCatamaranPret(self):
        return f"Le catamaran {self.nom} de type {self.type_catamaran} est prêt à prendre la mer !"

    def trouverNbPassager(self):
        return random.randint(0, 15)

    def trouverUnEquipage(self):
        return random.randint(0, 8)




















