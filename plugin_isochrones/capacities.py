import requests


URL_CAPACITES = "https://data.geopf.fr/navigation/getcapabilities"

# Choix utilisés si capacities ne marche pas
DEFAUTS = {
    "resource": ["bdtopo-valhalla", "bdtopo-pgr"],
    "profile": ["car", "pedestrian"],
    "costType": ["time", "distance"],
    "direction": ["departure", "arrival"],
    "timeUnit": ["second", "minute", "hour"],
    "distanceUnit": ["meter", "kilometer"],
}

CONTRAINTES_DEFAUT = {"waytype": ["autoroute", "tunnel", "pont"]}


class Capacites:

    def __init__(self, donnees=None):
        
        """        
        Entrées :
            - donnees  : données récupérées depuis le service de la Géoplateforme.
        """
        self.donnees = donnees
        self.lues = donnees is not None

    @classmethod
    def charger(cls):
        """        
        Entrées :
            - cls : référence à la classe Capacites.                
        Sortie :
            - Capacites : instance contenant les données récupérées
              ou None si la récupération a échoué.
        """
        try:
            reponse = requests.get(URL_CAPACITES, timeout=10)
            reponse.raise_for_status()
            return cls(reponse.json())
        except Exception:
            return cls(None)

    def ressources(self):
        """
       Entrées :
           - self : objet Capacites contenant les données du service.
       Sortie :
           - list : liste des identifiants des ressources proposant
             le calcul d'isochrones.
        """

        if not self.lues:
            return list(DEFAUTS["resource"])

        ressources = [
            r["id"] for r in self.donnees.get("resources", [])
            if any(
                op["id"] == "isochrone"
                for op in r.get("availableOperations", [])
            )
        ]

        return ressources or list(DEFAUTS["resource"])

    def parametres(self, ressource=None):
        """
        Entrées :
            - self : objet Capacites contenant les données du service.
            - ressource : identifiant de la ressource
              concernée. Si None, utilise la première ressource disponible.
        Sortie :
            - dict : dictionnaire associant le nom de chaque paramètre
              à ses valeurs possibles.
        """

        if not self.lues:
            return {}

        ressource = ressource or self.ressources()[0]
        for r in self.donnees.get("resources", []):
            if r["id"] == ressource:
                for op in r.get("availableOperations", []):
                    if op["id"] == "isochrone":
                        return {
                            p["id"]: p.get("values")
                            for p in op.get("availableParameters", [])
                        }

        return {}

    def valeurs(self, nom, ressource=None):
        
        """        
        Entrées :
            - self : objet Capacites.
            - nom : identifiant du paramètre recherché
            - ressource : identifiant de la ressource
              concernée. Par défaut, None.

        Sortie :
            - list : liste des valeurs possibles pour le paramètre demandé.
        """

        valeurs = self.parametres(ressource).get(nom)

        if isinstance(valeurs, list):
            return valeurs

        return list(DEFAUTS.get(nom, []))

    def contraintes(self, ressource=None):
        """
       Entrées :
           - self : objet Capacites.
           - ressource : identifiant de la ressource
             concernée. Par défaut, None.
       Sortie :
           - dict : dictionnaire associant chaque clé de contrainte
             à la liste de ses valeurs possibles
       """
        contraintes = self.parametres(ressource).get("constraints")

        if not isinstance(contraintes, dict):
            return dict(CONTRAINTES_DEFAUT)

        return {
            c["key"]: c["values"]
            for c in contraintes.get("keys", [])
            if c.get("values")
        }