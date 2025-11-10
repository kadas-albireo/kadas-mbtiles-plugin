# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
import os
import sys

from . import resources
from .kadas_gpkg_export import KadasGpkgExport
from qgis.gui import *
from kadas.kadasgui import *





class KadasGpkg(QObject):

    def __init__(self, iface):
        QObject.__init__(self)

        self.iface = KadasPluginInterface.cast(iface)

        # initialize locale
        if QSettings().value('locale/userLocale'):
            self.locale = QSettings().value('locale/userLocale')[0:2]
            locale_path = os.path.join(
                os.path.dirname(__file__),
                'i18n',
                'kadas_gpkg_{}.qm'.format(self.locale))

            if os.path.exists(locale_path):
                self.translator = QTranslator()
                self.translator.load(locale_path)
                QCoreApplication.installTranslator(self.translator)

        self.kadasGpkgExport = KadasGpkgExport(self.iface)

    def initGui(self):

        self.menu = QMenu()

        self.exportShortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_E, Qt.CTRL + Qt.Key_M), self.iface.mainWindow())
        self.exportShortcut.activated.connect(self.__exportGpkg)
        self.exportAction = QAction(self.tr("GPKG Export"))
        self.exportAction.triggered.connect(self.__exportGpkg)
        self.menu.addAction(self.exportAction)

        self.iface.addActionMenu(self.tr("MBTILES"),
                                 QIcon(":/plugins/KADASGpkg/icons/gpkg.png"),
                                 self.menu,
                                 self.iface.PLUGIN_MENU,
                                 self.iface.MAPS_TAB)

        # self.action = QAction('Go!', self.iface.mainWindow())
        # self.action.triggered.connect(lambda : print("Go!"))
        # self.iface.addToolBarIcon(self.action)




    def unload(self):
        self.iface.removeActionMenu(self.menu, self.iface.PLUGIN_MENU, self.iface.MAPS_TAB)


    def __exportGpkg(self):
        self.kadasGpkgExport.run()
