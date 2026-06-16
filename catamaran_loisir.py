from catamaran import Catamaran


class CatamaranLoisir(Catamaran):
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
        voile_loisir,
        coque_rotomoule
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

        self.voile_loisir = voile_loisir
        self.coque_rotomoule = coque_rotomoule

    def get_voile_loisir(self):
        return self.voile_loisir

    def get_coque_rotomoule(self):
        return self.coque_rotomoule

    def set_voile_loisir(self, voile_loisir):
        self.voile_loisir = voile_loisir

    def set_coque_rotomoule(self, coque_rotomoule):
        self.coque_rotomoule = coque_rotomoule

    def traiterEquipageCatamaran_loisir(self, nb_equipage=None):
        if nb_equipage is None:
            nb_equipage = self.trouverUnEquipage()

        return 1 <= nb_equipage <= 3

    def traiterPassagersCatamaran_loisirs(self, nb_passagers=None):
        if nb_passagers is None:
            nb_passagers = self.trouverNbPassager()

        return 1 <= nb_passagers <= 12

    def afficherCaracteristiqueCatamaran_loisir(self):
        data = self.afficheCaracteristiquesCatamaran("Loisir")
        if data is None:
            return None

        data["voile_loisir"] = self.voile_loisir
        data["coque_rotomoule"] = self.coque_rotomoule
        return data