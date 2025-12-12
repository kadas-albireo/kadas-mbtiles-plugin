# -*- coding: utf-8 -*-


def classFactory(iface):
    from .kadas_mbtiles import KadasMBtiles

    return KadasMBtiles(iface)
