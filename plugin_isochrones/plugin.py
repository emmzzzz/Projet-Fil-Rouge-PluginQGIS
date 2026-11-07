from qgis.PyQt.QtWidgets import QAction
import os
from .interface import Interface
from qgis.PyQt.QtGui import QIcon

class IsochronePlugin:

    def __init__(self, iface):
        """Constructor.
        Args:
            iface: An interface instance that provides the hook to QGIS.
        """
        self.iface = iface
        self.action = None
        self.dialog = None

          
    def initGui(self):
        """ Create the menu entries and toolbar icons inside the QGIS GUI."""

        dossier_plugin = os.path.dirname(__file__)
        chemin_icone = os.path.join(dossier_plugin, "icone.jpg")
        icon = QIcon(chemin_icone)
        
        self.action = QAction(icon,"Calcul d'isochrones",self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&Isochrones Géoplateforme", self.action)
        self.iface.addToolBarIcon(self.action)
        
    

    

    def unload(self):
        """Remove the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu("&Isochrones Géoplateforme", self.action)
        self.iface.removeToolBarIcon(self.action)

    
    def run(self):
        if self.dialog is None:
            self.dialog = Interface(self.iface)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()