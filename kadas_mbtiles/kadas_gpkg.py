# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
import os
import sys

from . import resources
from .kadas_gpkg_export import KadasGpkgExport, KadasMBTilesExportDialog
from qgis.gui import *
from kadas.kadasgui import *

from qgis.core import QgsApplication
from qgis.analysis import QgsNativeAlgorithms



class KadasGpkg(QObject):

    def __init__(self, iface):
        QObject.__init__(self)

        self.iface = KadasPluginInterface.cast(iface)

        self.KadasMBTilesExportDialog = None

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


        self.exportShortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_E, Qt.CTRL + Qt.Key_M), self.iface.mainWindow())
        self.exportShortcut.activated.connect(self.__exportGpkg)
        self.exportAction = QAction(QIcon(":/plugins/KADASGpkg/icons/mbtiles_export.png"), self.tr("Export MBTiles"))
        self.exportAction.triggered.connect(self.__exportGpkg)

        self.iface.addAction(self.exportAction, self.iface.PLUGIN_MENU, self.iface.GPS_TAB)

        # self.action = QAction('Go!', self.iface.mainWindow())
        # self.action.triggered.connect(lambda : print("Go!"))
        # self.iface.addToolBarIcon(self.action)

        QgsApplication.instance().processingRegistry().addProvider(QgsNativeAlgorithms())




    def unload(self):
        self.iface.removeAction(self.exportAction, self.iface.PLUGIN_MENU, self.iface.GPS_TAB)

    def __exportGpkg(self):
        # self.kadasGpkgExport.run()

        # Check dialog already open
        if self.KadasMBTilesExportDialog is not None:
            return

        self.KadasMBTilesExportDialog = KadasMBTilesExportDialog(self.iface.mainWindow(), self.iface)
        self.KadasMBTilesExportDialog.exec()

        #TODO do make non modal
        self.KadasMBTilesExportDialog.finished.connect(lambda: print("Dialog closed"))
        self.KadasMBTilesExportDialog = None
