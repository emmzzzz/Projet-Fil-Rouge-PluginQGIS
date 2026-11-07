def classFactory(iface):
    """
    Args:
        iface: A QGIS interface instance.

    Returns:
        Plugin: The plugin instance.
    """
    from .plugin import IsochronePlugin
    return IsochronePlugin(iface)