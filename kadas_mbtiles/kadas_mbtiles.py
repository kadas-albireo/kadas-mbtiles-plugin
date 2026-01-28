# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
import os

from .kadas_mbtiles_export_dialog import KadasMBTilesExportDialog
from qgis.gui import *
from kadas.kadasgui import *

from qgis.core import QgsApplication
from qgis.analysis import QgsNativeAlgorithms


class KadasMBtiles(QObject):

    def __init__(self, iface):
        QObject.__init__(self)

        self.iface = KadasPluginInterface.cast(iface)

        self.KadasMBTilesExportDialog = None

        # initialize locale
        if QSettings().value("locale/userLocale"):
            self.locale = QSettings().value("locale/userLocale")[0:2]
            locale_path = os.path.join(
                os.path.dirname(__file__),
                "i18n",
                "kadas_mbtiles_{}.qm".format(self.locale),
            )

            if os.path.exists(locale_path):
                self.translator = QTranslator()
                self.translator.load(locale_path)
                QCoreApplication.installTranslator(self.translator)

    def initGui(self):

        self.exportShortcut = QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_E, Qt.CTRL + Qt.Key_M),
            self.iface.mainWindow(),
        )
        self.exportShortcut.activated.connect(self.__exportMbtiles)
        self.exportAction = QAction(
            QIcon(":/plugins/KADASMbtiles/icons/mbtiles_export.png"),
            self.tr("Export MBTiles"),
        )
        self.exportAction.triggered.connect(self.__exportMbtiles)

        self.iface.addAction(
            self.exportAction, self.iface.PLUGIN_MENU, self.iface.MAPS_TAB
        )

        QgsApplication.instance().processingRegistry().addProvider(
            QgsNativeAlgorithms()
        )

    def unload(self):
        self.iface.removeAction(
            self.exportAction, self.iface.PLUGIN_MENU, self.iface.MAPS_TAB
        )

    def __exportMbtiles(self):

        # Check dialog already open
        if self.KadasMBTilesExportDialog is not None:
            return

        self.KadasMBTilesExportDialog = KadasMBTilesExportDialog(
            self.iface.mainWindow(), self.iface
        )
        self.KadasMBTilesExportDialog.show()
        self.KadasMBTilesExportDialog.finished.connect(self.__dialogFinished)

    def __dialogFinished(self, result):
        self.KadasMBTilesExportDialog.finished.disconnect()
        self.KadasMBTilesExportDialog.clear()
        self.KadasMBTilesExportDialog = None
