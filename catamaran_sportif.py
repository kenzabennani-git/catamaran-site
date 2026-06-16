from catamaran import Catamaran


class CatamaranSportif(Catamaran):
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
        categorie_type_B,
        foc,
        derives_pivotantes,
        grande_voile
    ):
        super().__init__(
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
        )

        self.foc = foc
        self.derives_pivotantes = derives_pivotantes
        self.grande_voile = grande_voile

    def get_foc(self):
        return self.foc

    def get_derives_pivotantes(self):
        return self.derives_pivotantes

    def get_grande_voile(self):
        return self.grande_voile

    def set_foc(self, foc):
        self.foc = foc

    def set_derives_pivotantes(self, derives_pivotantes):
        self.derives_pivotantes = derives_pivotantes

    def set_grande_voile(self, grande_voile):
        self.grande_voile = grande_voile

    def traiterEquipageCatamaran_sportif(self, nb_equipage=None):
        if nb_equipage is None:
            nb_equipage = self.trouverUnEquipage()

        return 1 <= nb_equipage <= 6

    def afficherCaracteristiqueCatamaran_sportif(self):
        data = self.afficheCaracteristiquesCatamaran("Sportif")
        if data is None:
            return None

        data["foc"] = self.foc
        data["derives_pivotantes"] = self.derives_pivotantes
        data["grande_voile"] = self.grande_voile
        return data