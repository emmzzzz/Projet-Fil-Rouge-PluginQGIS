import requests

# Adresse de l'API de la GéoPlateforme 
URL= "https://data.geopf.fr/navigation/isochrone"


class Geoplateforme:

    def calculer_isochrone(self, parametres):
        """
        Entrée :
            parametres : dictionnaire contenant les informations
            nécessaires au calcul de l'isochrone (coordonnées,
            temps de déplacement, mode de transport)
        
        Sortie :
            resultat : dictionnaire contenant les données JSON
            renvoyées par l'API
        """

        try:
            response = requests.get(URL, params=parametres, timeout=None)
        except requests.RequestException as erreur:
            raise ConnectionError(f"Impossible de joindre le service : {erreur}")

        if not response.ok:
            raise ValueError(
                f"Erreur HTTP :{response.text[:300]}")

        try:
            resultat = response.json()
        except ValueError:
            raise ValueError("La réponse du service n'est pas du JSON.")

        return resultat