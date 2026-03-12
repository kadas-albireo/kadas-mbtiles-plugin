# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QObject, QSettings, QCoreApplication, QTranslator, Qt
from qgis.PyQt.QtGui import QAction, QIcon, QKeySequence

from qgis.PyQt.QtWidgets import QShortcut
import os

from .kadas_mbtiles_export_dialog import KadasMBTilesExportDialog
from kadas.kadasgui import KadasPluginInterface

from qgis.core import QgsApplication
from qgis.analysis import QgsNativeAlgorithms

PLUGIN_DIR = os.path.dirname(__file__)

class KadasMBtiles(QObject):

    def __init__(self, iface):
        QObject.__init__(self)

        self.iface = KadasPluginInterface.cast(iface)

        self.KadasMBTilesExportDialog = None

        # initialize locale
        if QSettings().value("locale/userLocale"):
            self.locale = QSettings().value("locale/userLocale")[0:2]
            locale_path = os.path.join(
                PLUGIN_DIR,
                "i18n",
                "kadas_mbtiles_{}.qm".format(self.locale),
            )

            if os.path.exists(locale_path):
                self.translator = QTranslator()
                self.translator.load(locale_path)
                QCoreApplication.installTranslator(self.translator)

    def initGui(self):

        self.exportShortcut = QShortcut(
            QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_E, Qt.Modifier.CTRL | Qt.Key.Key_M),
            self.iface.mainWindow(),
        )
        self.exportShortcut.activated.connect(self.__exportMbtiles)
        self.exportAction = QAction(
            QIcon( os.path.join(PLUGIN_DIR, "icons", "mbtiles_export.png") ),
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
