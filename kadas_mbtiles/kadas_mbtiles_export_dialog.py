import os
from pathlib import Path

from qgis.PyQt.QtCore import QSettings, Qt, QFile
from qgis.PyQt.QtGui import QPixmap, QColor
from qgis.PyQt.QtWidgets import (
    QDialog,
    QFileDialog,
    QDialogButtonBox,
    QMessageBox,
    QProgressDialog,
)
from qgis.PyQt.uic import loadUiType

from qgis.gui import QgsExtentWidget

from qgis.core import Qgis, QgsRectangle, QgsProject

from qgis.core import QgsApplication, QgsProcessingContext, QgsProcessingFeedback
from qgis.analysis import QgsNativeAlgorithms

# from .kadas_gpkg_layer_list import KadasGpkgLayersList
from kadas.kadasgui import KadasMapToolSelectRect

WidgetUi, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), "kadas_mbtiles_export_dialog.ui")
)


class KadasMBTilesExportDialog(QDialog, WidgetUi):

    def __init__(self, parent, iface):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.iface = iface

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        # self.mExtentGroupBox
        extent = QgsExtentWidget()

        self.mGroupBox.layout().addWidget(extent)
        #     self.spinBoxExportScale.setValue(int(iface.mapCanvas().mapSettings().scale()))

        self.buttonSelectFile.clicked.connect(self.__selectOutputFile)
        #     self.checkBoxClear.toggled.connect(self.__updateLocalLayerList)
        #     self.checkBoxExportScale.toggled.connect(self.spinBoxExportScale.setEnabled)

        #     self.mGroupBoxExtent.toggled.connect(self.__extentToggled)

        mapSettings = iface.mapCanvas().mapSettings()

        self.mExtentGroupBox.setOutputCrs(mapSettings.destinationCrs())
        self.mExtentGroupBox.setCurrentExtent(
            mapSettings.visibleExtent(), mapSettings.destinationCrs()
        )
        self.mExtentGroupBox.setOutputExtentFromCurrent()
        self.mExtentGroupBox.setMapCanvas(iface.mapCanvas())
        """
            // Use unrotated visible extent to insure output size and scale matches canvas
        QgsMapSettings ms = mMapCanvas->mapSettings();
        ms.setRotation( 0 );
        mExtent = ms.visibleExtent();
        mSize = ms.outputSize();

        mExtentGroupBox->setOutputCrs( ms.destinationCrs() );
        mExtentGroupBox->setCurrentExtent( mExtent, ms.destinationCrs() );
        mExtentGroupBox->setOutputExtentFromCurrent();
        mExtentGroupBox->setMapCanvas( mapCanvas );
        """

    #     self.mRectTool = KadasMapToolSelectRect(iface.mapCanvas())
    #     self.mRectTool.rectChanged.connect(self.__extentChanged)
    #     iface.mapCanvas().setMapTool(self.mRectTool)

    #     self.labelCheckIcon.setPixmap(QPixmap(":/images/themes/default/mIconSuccess.svg"))
    #     self.labelWarnIcon.setPixmap(QPixmap(":/images/themes/default/mIconWarning.svg"))

    def outputFile(self):
        return self.lineEditOutputFile.text()

    def minZoom(self):
        return self.minZoomSpinBox.value()

    def maxZoom(self):
        return self.maxZoomSpinBox.value()

    def DPI(self):
        return self.DPISpinBox.value()

    def antialiasing(self):
        return self.checkBoxAntialiasing.value()

    def metatileSize(self):
        return self.metaTileSizeSpinBox.value()

    # def clearOutputFile(self):
    #     return self.checkBoxClear.isChecked()

    # def selectedLayers(self):
    #     return self.listWidgetLayers.getSelectedLayers()

    # def buildPyramids(self):
    #     return self.checkBoxPyramids.isChecked()

    # def rasterExportScale(self):
    #     return self.spinBoxExportScale.value() if self.checkBoxExportScale.isChecked() else None

    # def filterExtent(self):
    #     if not self.mGroupBoxExtent.isChecked():
    #         return None

    #     return self.mRectTool.rect()

    # def filterExtentCrs(self):
    #     if not self.mGroupBoxExtent.isChecked():
    #         return None

    #     return self.iface.mapCanvas().mapSettings().destinationCrs()

    # def clear(self):
    #     self.iface.mapCanvas().unsetMapTool(self.mRectTool)
    #     self.mRectTool = None

    def __selectOutputFile(self):
        lastDir = QSettings().value("/UI/lastImportExportDir", ".")
        filename = QFileDialog.getSaveFileName(
            self,
            self.tr("Select MBTiles File..."),
            lastDir,
            self.tr("MBTiles files (*.mbtiles *.MBTILES)"),
            "",
            QFileDialog.DontConfirmOverwrite,
        )[0]
        if not filename:
            return

        if not filename.lower().endswith(".mbtiles"):
            filename += ".mbtiles"

        QSettings().setValue("/UI/lastImportExportDir", os.path.dirname(filename))
        self.lineEditOutputFile.setText(filename)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(filename is not None)
        # self.__updateLocalLayerList()

    # def __updateLocalLayerList(self):
    #     self.listWidgetLayers.updateLayerList(self.lineEditOutputFile.text() if not self.checkBoxClear.isChecked() else None)

    # def __extentToggled(self, checked):
    #     if checked:
    #         self.mRectTool.setRect( self.iface.mapCanvas().extent() )
    #     else:
    #         self.mRectTool.clear()

    # def __extentChanged(self, extent):
    #     if extent.isNull():
    #         self.mLineEditXMin.setText("")
    #         self.mLineEditYMin.setText("")
    #         self.mLineEditXMax.setText("")
    #         self.mLineEditYMax.setText("")
    #     else:
    #         decs = 0
    #         if self.iface.mapCanvas().mapSettings().mapUnits() == Qgis.DistanceUnit.Degrees:
    #             decs = 3
    #         self.mLineEditXMin.setText(f"{extent.xMinimum(): {decs}f}")
    #         self.mLineEditYMin.setText(f"{extent.yMinimum(): {decs}f}")
    #         self.mLineEditXMax.setText(f"{extent.xMaximum(): {decs}f}")
    #         self.mLineEditYMax.setText(f"{extent.yMaximum(): {decs}f}")

    def accept(self):

        alg = (
            QgsApplication.instance()
            .processingRegistry()
            .createAlgorithmById("native:tilesxyzmbtiles")
        )
        print("deux")

        if QFile.exists(self.outputFile()()):
            ret = QMessageBox.question(
                self,
                self.tr("MBTiles already exists"),
                self.tr(
                    f"The file '{self.outputFile()()}' already exists. Do you want to overwrite it?"
                ),
                QMessageBox.Cancel | QMessageBox.Yes,
                QMessageBox.Cancel,
            )
            if ret != QMessageBox.Yes:
                # Cancel export
                return

        params = {
            "EXTENT": self.mExtentGroupBox.outputExtent(),
            "ZOOM_MIN": 12,  # self.project_configuration.base_map_tiles_min_zoom_level,
            "ZOOM_MAX": 14,  # self.project_configuration.base_map_tiles_max_zoom_level,
            "TILE_SIZE": 2,
            "OUTPUT_FILE": self.outputFile()(),
        }

        params = {
            "EXTENT": self.mExtentGroupBox.outputExtent(),  # '5.447916487,10.614400411,44.911718236,48.736628986 [EPSG:4326]',
            "ZOOM_MIN": self.minZoom(),
            "ZOOM_MAX": self.maxZoom(),
            "DPI": self.DPI(),
            "BACKGROUND_COLOR": QColor(0, 0, 0, 0),
            "ANTIALIAS": self.antialiasing(),
            "TILE_FORMAT": 0,  # Always  PNG - 0
            #    'QUALITY':75,
            "METATILESIZE": 4,
            "OUTPUT_FILE": self.outputFile()(),  # 'C:/Users/Valentin/Documents/out_qgis.mbtiles'
        }

        context = QgsProcessingContext()
        context.setProject(QgsProject.instance())
        _feedback = QgsProcessingFeedback()
        print("deux et demi")

        # processing.run("native:tilesxyzmbtiles", )

        # The "native:tilesxyzmbtiles" would fail if a file is already existing
        try:
            os.remove(self.outputFile()())
        except OSError:
            pass

        print("before run")

        progressDialog = QProgressDialog(
            "Exporting to MBTiles...", "Cancel", 0, 100, self
        )
        progressDialog.setWindowModality(Qt.WindowModal)

        QgsApplication.setOverrideCursor(Qt.WaitCursor)

        _feedback.progressChanged.connect(
            lambda progress: progressDialog.setValue(int(progress))
        )
        progressDialog.canceled.connect(lambda: _feedback.cancel())

        progressDialog.show()
        res, ok = alg.run(params, context, _feedback)
        QgsApplication.restoreOverrideCursor()
        progressDialog.close()

        print("after run")
        print("trois")
        if not ok:
            QMessageBox.critical(
                self,
                self.tr("MBTiles Export failed"),
                self.tr("Failed to create mbtiles file:\n")
                + str(_feedback.textLog())
                + str(res),
            )
            return False

        super().accept()
