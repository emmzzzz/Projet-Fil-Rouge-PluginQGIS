import json
import tempfile
from qgis.core import QgsVectorLayer, QgsProject

class Resultat:

    def __init__(self, donnees):
        """
        Entrées :
            - donnees : dictionnaire contenant les paramètre
            """

        self.donnees = donnees
        self.geometry = donnees["geometry"]

    def obtenir_geojson(self):
        
        """
        Entrées :
            - self : objet contenant les données et la géométrie de l'isochrone.
        Sortie :
            - geojson : dictionnaire Python structuré au format GeoJSON
        """
        
        feature = {
            "type": "Feature",
            "properties": {
                "point": self.donnees["point"],
                "resource": self.donnees["resource"],
                "resourceVersion": self.donnees.get("resourceVersion"),
                "costType": self.donnees["costType"],
                "costValue": self.donnees["costValue"],
                "profile": self.donnees["profile"],
                "direction": self.donnees["direction"]
            },
            "geometry": self.geometry
        }
        geojson = {
            "type": "FeatureCollection",
            "features": [feature]
        }
        return geojson



    def ajouter_a_qgis(self, iface, nom="Isochrone"):
        
        """
        Entrées :
            - self : objet contenant les paramètres
            - iface : interface QGIS permettant d'interagir avec le projet et la carte.
            - nom  : nom attribué à la couche dans QGIS.
        Sortie :
            - couche : couche vectorielle ajoutée au projet QGIS.
        """
        
        geojson = self.obtenir_geojson()
        # Fichier temporaire
        tmp = tempfile.NamedTemporaryFile(suffix=".geojson",delete=False,mode="w",encoding="utf-8")
        json.dump(geojson,tmp,ensure_ascii=False,indent=4)
        tmp.close()

        couche = QgsVectorLayer(tmp.name, nom, "ogr")

        if not couche.isValid():
            raise ValueError("La couche n'a pas pu être chargée dans QGIS.")

        couche.setOpacity(0.6)

        QgsProject.instance().addMapLayer(couche)

        iface.setActiveLayer(couche)
        iface.zoomToActiveLayer()

        return couche