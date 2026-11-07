from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QPushButton,
    QMessageBox,
    QLabel,
    QApplication,
    QCheckBox,
    QGroupBox
)

from qgis.PyQt.QtCore import Qt

from .parametres import Parametres
from .geoplateforme import Geoplateforme
from .resultats import Resultat
from .capacities import Capacites


VALEURS_DEFAUT = {
    "second": 300,
    "minute": 5,
    "hour": 1,
    "meter": 1000,
    "kilometer": 1,
}


class Interface(QDialog):

    def __init__(self, iface):
        """        
        Entrées :
            - iface : interface principale de QGIS
        """

        super().__init__(iface.mainWindow())

        self.iface = iface

        self.setWindowTitle("Calcul d'isochrones")

        self.setMinimumWidth(420)
        self.api = Geoplateforme()
        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            self.capacites = Capacites.charger()
        finally:
            QApplication.restoreOverrideCursor()

        self.creer_interface()

        if not self.capacites.lues:
            self.iface.messageBar().pushWarning(
                "Isochrones",
                "Capacités du service non lues : "
                "valeurs par défaut utilisées."
            )


    # Construction de l'interface

    def remplir(self, combo, valeurs, choisi=None):
        """
        Entrées :
            - combo : liste déroulante QComboBox à remplir.
            - valeurs : liste des valeurs à ajouter.
            - choisi : valeur à sélectionner par défaut.Si None, conserve la sélection précédente.
        Sortie :
            - Met à jour la liste déroulante.
        """

        precedent = choisi if choisi is not None else combo.currentData()

        combo.blockSignals(True)
        combo.clear()

        for valeur in valeurs:
            combo.addItem(str(valeur), valeur)

        index = combo.findData(precedent)

        if index >= 0:
            combo.setCurrentIndex(index)

        combo.blockSignals(False)

    def creer_interface(self):
        """
        Entrées :
            - self : instance de la classe Interface.
        Sortie :
            - Affiche et organise tous les éléments de l'interface.
        """


        layout = QVBoxLayout()
        self.form = QFormLayout()
        form = self.form

        # Coordonnées par default
        self.longitude = QLineEdit("2.337306")
        self.latitude = QLineEdit("48.849319")


        form.addRow("Longitude :", self.longitude)
        form.addRow("Latitude :", self.latitude)

        # Ressource
        self.resource = QComboBox()
        self.remplir(self.resource, self.capacites.ressources())
        self.resource.currentIndexChanged.connect(
            self.maj_options_ressource
        )
        form.addRow("Ressource :", self.resource)

        # Type de calcul, profil, direction (remplis selon la ressource)
        self.cost_type = QComboBox()
        self.cost_type.currentIndexChanged.connect(self.maj_unites)
        form.addRow("Type de calcul :", self.cost_type)

        self.profile = QComboBox()
        form.addRow("Profil :", self.profile)

        self.direction = QComboBox()
        form.addRow("Direction :", self.direction)

        # Unités
        self.unite_temps = QComboBox()
        self.remplir(
            self.unite_temps,
            self.capacites.valeurs("timeUnit"),
            choisi="second"
        )
        self.unite_temps.currentIndexChanged.connect(
            self.maj_valeur_defaut
        )
        form.addRow("Unité de temps :", self.unite_temps)

        self.unite_distance = QComboBox()
        self.remplir(
            self.unite_distance,
            self.capacites.valeurs("distanceUnit"),
            choisi="meter"
        )
        self.unite_distance.currentIndexChanged.connect(
            self.maj_valeur_defaut
        )
        form.addRow("Unité de distance :", self.unite_distance)

        # Valeur du coût
        self.cost_value = QSpinBox()
        self.cost_value.setRange(1, 100000)
        self.cost_value.setValue(300)

        self.cost_label = QLabel(
            "Durée maximale :"
        )

        form.addRow(
            self.cost_label,
            self.cost_value
        )

        layout.addLayout(form)

        # Contraintes (types de voies à éviter)
        self.cases_contraintes = {}

        groupe = QGroupBox("Contraintes : éviter")
        layout_contraintes = QVBoxLayout()

        for valeur in self.capacites.contraintes().get("waytype", []):
            case = QCheckBox(str(valeur))
            layout_contraintes.addWidget(case)
            self.cases_contraintes[valeur] = case

        groupe.setLayout(layout_contraintes)
        layout.addWidget(groupe)

        # Bouton de calcul
        self.calculate_button = QPushButton(
            "Calculer"
        )

        self.calculate_button.clicked.connect(
            self.calculer
        )

        layout.addWidget(self.calculate_button)

        self.setLayout(layout)

        # Premier remplissage dépendant de la ressource
        self.maj_options_ressource()


    # Mises à jour dynamiques

    def maj_options_ressource(self):
        """
        Entrées :
            - self : instance de la classe Interface.
        Sortie :
            - Met à jour les listes déroulantes de l'interface.
        """

        ressource = self.resource.currentData()

        self.remplir(
            self.profile,
            self.capacites.valeurs("profile", ressource)
        )

        self.remplir(
            self.cost_type,
            self.capacites.valeurs("costType", ressource)
        )

        self.remplir(
            self.direction,
            self.capacites.valeurs("direction", ressource)
        )

        self.maj_unites()

    def est_temps(self):
        """        
        Entrées :
            - self : instance de la classe Interface.
        Sortie :
            - bool : True si le calcul est considéré comme un calcul
              en temps, False s'il s'agit d'un calcul en distance.
        """
        return self.cost_type.currentData() != "distance"

    def maj_unites(self):   
        """
        Entrées :
            - self : instance de la classe Interface.
        Sortie :
            - Actualise l'affichage des unités dans l'interface.
        """
        est_temps = self.est_temps()

        self.afficher_ligne(self.unite_temps, est_temps)
        self.afficher_ligne(self.unite_distance, not est_temps)
        self.maj_valeur_defaut()

    def afficher_ligne(self, widget, visible):
        """
       Entrées :
           - widget : élément graphique à afficher ou masquer.
           - visible : True pour afficher le champ,False pour le masquer.
       Sortie :
           - Modifie la visibilité du champ et de son libellé.
       """

        etiquette = self.form.labelForField(widget)

        if etiquette is not None:
            etiquette.setVisible(visible)

        widget.setVisible(visible)

    def maj_valeur_defaut(self):
        """
       Entrées :
           - self : instance de la classe Interface.
           - Aucune autre entrée.
       Sortie :
           - Actualise le libellé et la valeur du coût dans l'interface.
       """

        if self.est_temps():
            nature = "Durée"
            unite = self.unite_temps.currentData()
        else:
            nature = "Distance"
            unite = self.unite_distance.currentData()

        self.cost_label.setText(
            f"{nature} maximale ({unite}) :"
        )

        self.cost_value.setValue(VALEURS_DEFAUT.get(unite, 1))

    # Calcul

    def recuperer_contraintes(self):
        """
        Entrées :
            - self : instance de la classe Interface.
        Sortie :
            - list : liste des contraintes sélectionnées sous forme
              de dictionnaires ou une liste vide est retournée si aucune contrainte n'est cochée.
        """

        return [
            {
                "constraintType": "banned",
                "key": "wayType",
                "operator": "=",
                "value": valeur
            }
            for valeur, case in self.cases_contraintes.items()
            if case.isChecked()
        ]

    def recuperer_parametres(self):
        """        
        Entrées :
            - self : instance de la classe Interface
        Sortie :
            - Parametres : objet contenant l'ensemble des paramètres
        """

        return Parametres(
            longitude=self.longitude.text(),
            latitude=self.latitude.text(),
            resource=self.resource.currentData(),
            cost_type=self.cost_type.currentData(),
            cost_value=self.cost_value.value(),
            profile=self.profile.currentData(),
            direction=self.direction.currentData(),
            time_unit=self.unite_temps.currentData(),
            distance_unit=self.unite_distance.currentData(),
            constraints=self.recuperer_contraintes()
        )

    def calculer(self):
        """
        Lance le calcul de l'isochrone, récupère le résultat et l'ajoute
        au projet QGIS.

        Entrées :
            - self : instance de la classe Interface.

        Sortie :
            - Le résultat est ajouté sous forme de couche vectorielle
              au projet QGIS.
        """

        self.calculate_button.setEnabled(False)
        self.calculate_button.setText(
            "Calcul en cours..."
        )

        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:

            # 1. Récupération et validation des paramètres
            parametres = self.recuperer_parametres()

            dictionnaire = parametres.vers_dict()

            # 2. Appel de la Géoplateforme
            donnees = self.api.calculer_isochrone(
                dictionnaire
            )

            # 3. Création de l'objet résultat
            resultat = Resultat(donnees)

            # 4. Ajout de la couche à la carte QGIS
            if parametres.cost_type == "time":
                unite = parametres.time_unit
            else:
                unite = parametres.distance_unit

            nom = f"Isochrone {parametres.cost_value} {unite}"

            resultat.ajouter_a_qgis(self.iface, nom)

            self.iface.messageBar().pushSuccess(
                "Isochrones",
                "La couche a été ajoutée à la carte."
            )

        except Exception as erreur:

            QMessageBox.critical(
                self,
                "Erreur",
                str(erreur)
            )

        finally:

            QApplication.restoreOverrideCursor()

            self.calculate_button.setEnabled(True)

            self.calculate_button.setText(
                "Calculer"
            )