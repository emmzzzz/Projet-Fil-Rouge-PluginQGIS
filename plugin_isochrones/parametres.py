import json


class Parametres:

    def __init__(self,longitude,latitude,resource,cost_type,cost_value,
    profile,direction,time_unit="second",distance_unit="meter",constraints=None
    ):
      
        """
        Entrées :
           longitude, latitude : coordonnées du point de départ.
           resource : ressource utilisée par l'API.
           cost_type : type de calcul (temps ou distance).
           cost_value : valeur du temps ou de la distance.
           profile : profil de déplacement.
           direction : sens du calcul (départ ou arrivée).
           time_unit : unité de temps (par défaut : seconde).
           distance_unit : unité de distance (par défaut : mètre).
           constraints : liste de contraintes facultatives.

       Sortie :
           Création d'un objet contenant les paramètres
       """

        self.longitude = float(str(longitude).replace(",", "."))
        self.latitude = float(str(latitude).replace(",", "."))


        self.resource = resource
        self.cost_type = cost_type
        self.cost_value = int(cost_value)
        self.profile = profile
        self.direction = direction

        self.time_unit = time_unit
        self.distance_unit = distance_unit

        self.constraints = constraints or [] 

    def valider(self):
        
        """
        Entrée :
            Les paramètres enregistrés dans l'objet Parametres
        
        Sortie :
            True si les paramètres sont valides sinon déclenche une ValueError
        """

        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude invalide")

        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude invalide")

        if not self.resource:
            raise ValueError("Aucune ressource sélectionnée")

        if self.cost_type not in ["time", "distance"]:
            raise ValueError("Aucun type de calcul sélectionné")

        if self.cost_value <= 0:
            raise ValueError("La valeur du coût doit être positive")

        if not self.profile:
            raise ValueError("Aucun profil sélectionné")

        return True

    def vers_dict(self):
        """
        Entrée :
            Les paramètres enregistrés dans l'objet Parametres
        
        Sortie :
            Un dictionnaire Python contenant les paramètres validés
        """

        self.valider()

        parametres = {
            "point": f"{self.longitude},{self.latitude}",
            "resource": self.resource,
            "costType": self.cost_type,
            "costValue": self.cost_value,
            "profile": self.profile,
            "direction": self.direction,
            "timeUnit": self.time_unit,
            "distanceUnit": self.distance_unit,
            "geometryFormat": "geojson",
            "crs": "EPSG:4326"
        }

        if self.constraints:
            # Plusieurs contraintes : séparées par "|"
            parametres["constraints"] = "|".join(
                json.dumps(c, separators=(",", ":"))
                for c in self.constraints
            )

        return parametres