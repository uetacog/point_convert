#!/usr/bin/python3

from PyQt5 import QtWidgets, uic
import sys
import mgrs
from os.path import expanduser
from pprint import pprint

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        self.m = mgrs.MGRS()
        self.mgrs = ""
        self.latd, self.lond = "", ""
        self.latdm, self.londm = "", ""
        self.latdms, self.londms = "", ""
        self.coord_formats = ["Decimal", "Decimal Min", "Decimal Min Sec", "MGRS"]

        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('point_convert.ui', self) # Load the .ui file
        self.set_format_dec()

        self.save = self.findChild(QtWidgets.QAction, "actionSave")
        self.save.triggered.connect(self.save_text)
        self.loadlog = self.findChild(QtWidgets.QAction, "actionImport")
        self.loadlog.triggered.connect(self.import_text)
        self.exit = self.findChild(QtWidgets.QAction, "actionExit")
        self.exit.triggered.connect(QtWidgets.QApplication.quit)
        self.info = self.findChild(QtWidgets.QAction, "actionFormats")
        self.info.triggered.connect(self.format_info)


        self.dec_bool = self.findChild(QtWidgets.QCheckBox, "decCheck")
        self.dec_bool.stateChanged.connect(self.decmode)
        self.decmin_bool = self.findChild(QtWidgets.QCheckBox, "decminCheck")
        self.decmin_bool.stateChanged.connect(self.decminmode)
        self.dms_bool = self.findChild(QtWidgets.QCheckBox, "dmsCheck")
        self.dms_bool.stateChanged.connect(self.dmsmode)
        self.mgrs_bool = self.findChild(QtWidgets.QCheckBox, "mgrsCheck")
        self.mgrs_bool.stateChanged.connect(self.mgrsmode)

        self.format_btn = self.findChild(QtWidgets.QPushButton, "format")
        self.format_btn.clicked.connect(self.set_format)

        self.l1 = self.findChild(QtWidgets.QLabel, "l1")
        self.l2 = self.findChild(QtWidgets.QLabel, "l2")
        self.i1 = self.findChild(QtWidgets.QLineEdit, "i1")
        self.i2 = self.findChild(QtWidgets.QLineEdit, "i2")
        self.tag = self.findChild(QtWidgets.QLineEdit, "tag")
        self.convert = self.findChild(QtWidgets.QPushButton, "convert")
        self.convert.clicked.connect(self.convert_coords)
        self.results = self.findChild(QtWidgets.QTextEdit, "results")
        self.show()

    def decmode(self):
        if self.dec_bool.isChecked():
            self.coord_formats.append("Decimal")
        else:
            self.coord_formats.remove("Decimal")
        self.set_format()

    def decminmode(self):
        if self.decmin_bool.isChecked():
            self.coord_formats.append("Decimal Min")
        else:
            self.coord_formats.remove("Decimal Min")
        self.set_format()

    def dmsmode(self):
        if self.dms_bool.isChecked():
            self.coord_formats.append("Decimal Min Sec")
        else:
            self.coord_formats.remove("Decimal Min Sec")
        self.set_format()

    def mgrsmode(self):
        if self.mgrs_bool.isChecked():
            self.coord_formats.append("MGRS")
        else:
            self.coord_formats.remove("MGRS")
        self.set_format()

    def set_format(self):
        sender = self.sender().isCheckable()
        self.i1.setStyleSheet("color: white;")
        self.i2.setStyleSheet("color: white;")
        self.dec_bool.setStyleSheet("color: white;")
        self.decmin_bool.setStyleSheet("color: white;")
        self.dms_bool.setStyleSheet("color: white;")
        self.mgrs_bool.setStyleSheet("color: white;")
        cur_btn = self.format_btn.text()
        if sender:
            return

        if cur_btn in self.coord_formats:
            next_coord = self.coord_formats.index(cur_btn) + 1
        else:
            if len(self.coord_formats) > 0:
                self.format_btn.setText(self.coord_formats[0])
                next_coord = 0
            else:
                self.dec_bool.setStyleSheet("color: red;")
                self.decmin_bool.setStyleSheet("color: red;")
                self.dms_bool.setStyleSheet("color: red;")
                self.mgrs_bool.setStyleSheet("color: red;")
                return

        if next_coord > len(self.coord_formats) - 1:
            next_coord = 0

        self.format_btn.setText(self.coord_formats[next_coord])
        cur_btn = self.format_btn.text()

        if cur_btn == "Decimal":
            self.set_format_dec()
        elif cur_btn == "Decimal Min":
            self.set_format_decmin()
        elif cur_btn == "Decimal Min Sec":
            self.set_format_decminsec()
        elif cur_btn == "MGRS":
            self.set_format_mgrs()

    def set_format_dec(self):
        self.l1.setText("Latitude")
        self.l2.setText("Longitude")
        self.i2.show()
        self.i1.setText("")
        self.i2.setText("")
        self.i1.setPlaceholderText("38.8977")
        self.i2.setPlaceholderText("-77.0365")

    def set_format_decmin(self):
        self.l1.setText("Latitude")
        self.l2.setText("Longitude")
        self.i2.show()
        self.i1.setText("")
        self.i2.setText("")
        self.i1.setPlaceholderText("38 53.86200")
        self.i2.setPlaceholderText("-77 02.19000")

    def set_format_decminsec(self):
        self.l1.setText("Latitude")
        self.l2.setText("Longitude")
        self.i2.show()
        self.i1.setText("")
        self.i2.setText("")
        self.i1.setPlaceholderText("38 53 51.7200")
        self.i2.setPlaceholderText("-77 02 11.4000")

    def set_format_mgrs(self):
        self.l1.setText("MGRS")
        self.l2.setText("")
        self.i2.hide()
        self.i1.setText("")
        self.i1.setPlaceholderText("18SUJ2339407395")

    def convert_coords(self):
        self.mgrs = self.i1.text()
        self.lat = self.i1.text()
        self.lon = self.i2.text()
        try:
            self.i1.setStyleSheet("color: white;")
            self.i2.setStyleSheet("color: white;")
            if self.format_btn.text() == "Decimal":
                self.convert_dec()
            elif self.format_btn.text() == "Decimal Min":
                self.convert_decmin()
            elif self.format_btn.text() == "Decimal Min Sec":
                self.convert_decminsec()
            else:
                self.convert_mgrs()
        except Exception as e:
            self.i1.setStyleSheet("color: red;")
            self.i2.setStyleSheet("color: red;")

    def convert_dec(self):
        # Degrees Lat Long 	34.6420885°, -077.2715427°
        # Degrees Minutes	34°38.52531', -077°16.29256'
        # Degrees Minutes Seconds 	34°38'31.5184", -077°16'17.5539"
        # MGRS	18STD9180035700


        self.latd = float(self.lat)
        self.lond = float(self.lon)
        latd, latm, lats = self.m.ddtodms(self.latd)
        lond, lonm, lons = self.m.ddtodms(self.lond)
        self.latdm = f"{int(self.latd)} {(latm + (lats / 60)):.4f}"
        self.londm = f"{int(self.lond)} {(lonm + (lons / 60)):.4f}"
        self.latdms = f"{int(latd)} {int(latm)} {lats:.4f}"
        self.londms = f"{int(lond)} {int(lonm)} {lons:.4f}"
        if "." in self.mgrs:
            self.mgrs = self.m.toMGRS(self.lat, self.lon)
        self.latd = f"{self.latd:.6f}"
        self.lond = f"{self.lond:.6f}"
        self.print_results()

    def convert_decmin(self):
        # Degrees Lat Long 	34.6420885°, -077.2715427°
        # Degrees Minutes	34°38.52531', -077°16.29256'
        # Degrees Minutes Seconds 	34°38'31.5184", -077°16'17.5539"
        # MGRS	18STD9180035700

        la = int(self.lat.split()[0])
        lo = int(self.lon.split()[0])
        latdec = float(self.lat.split()[1]) / 60
        londec = float(self.lon.split()[1]) / 60
        if la > 0:
            self.lat = float(self.lat.split()[0]) + latdec
        else:
            self.lat = float(self.lat.split()[0]) - latdec
        if lo > 0:
            self.lon = float(self.lon.split()[0]) + londec
        else:
            self.lon = float(self.lon.split()[0]) - londec
        self.convert_dec()

    def convert_decminsec(self):
        # Degrees Lat Long 	34.6420885°, -077.2715427°
        # Degrees Minutes	34°38.52531', -077°16.29256'
        # Degrees Minutes Seconds 	34°38'31.5184", -077°16'17.5539"
        # MGRS	18STD9180035700

        lat = float("".join(self.lat.split()))
        lon = float("".join(self.lon.split()))
        if lat > 0:
            lat = str(lat) + "N"
        else:
            lat = str(abs(lat)) + "S"
        if lon > 0:
            lon = str(lon) + "E"
        else:
            lon = str(abs(lon)) + "W"
        self.lat = self.m.dmstodd(lat)
        self.lon = self.m.dmstodd(lon)
        self.convert_dec()

    def convert_mgrs(self):
        # Degrees Lat Long 	34.6420885°, -077.2715427°
        # Degrees Minutes	34°38.52531', -077°16.29256'
        # Degrees Minutes Seconds 	34°38'31.5184", -077°16'17.5539"
        # MGRS	18STD9180035700
        milgrid = self.mgrs.replace(" ", "").encode()
        self.lat, self.lon = self.m.toLatLon(MGRS=milgrid)
        self.convert_dec()

    def print_results(self):
        old = self.results.toPlainText()
        string = ""

        dec = f"Decimal: \n" \
              f"    Lat: {self.latd} \n" \
              f"    Lon: {self.lond} \n"
        if self.dec_bool.isChecked():
            string = string + dec

        decmin =  f"Decimal Min: \n" \
                  f"    Lat: {self.latdm} \n" \
                  f"    Lon: {self.londm} \n"
        if self.decmin_bool.isChecked():
            string = string + decmin

        dms = f"Decimal Min Sec: \n" \
              f"    Lat: {self.latdms} \n" \
              f"    Lon: {self.londms} \n"
        if self.dms_bool.isChecked():
            string = string + dms

        mgrs = f"MGRS: \n" \
               f"    MGRS: {self.mgrs} \n"
        if self.mgrs_bool.isChecked():
            string = string + mgrs

        tag = f"Tag: \n" \
              f"    Tag: {self.tag.text()} \n"
        if self.tag.text() != "":
            string = string + tag

        results = f"{string}" \
                  f"-------------------------------------------------------------\n" \
                  f"{old}"
        self.results.setText(results)

    def save_text(self):
        log = self.results.toPlainText()
        homedir = expanduser("~/")
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save TXT", homedir, "TXT (*.txt)")
        if filename[-4:] != ".txt":
            filename = filename + ".txt"

        with open(filename, "w") as file:
            print(f"writing log to {filename}")
            file.write(log)

    def import_text(self):
        homedir = expanduser("~/")
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open TXT", homedir, "TXT (*.txt)")
        with open(filename) as file:
            txt = self.results.toPlainText()
            text = f"{txt} \n" \
                   f"{file.read()}"
            self.results.setText(text)

    def format_info(self):
        formatInfo = f"The following formats are expected; \n\n" \
                     f"Decimal: 34.6420885, -77.2715427 \n\n" \
                     f"Decimal Min: 34 38.52531, -77 16.29256 \n\n" \
                     f"Decimal Min Sec: 34 38 31.5184, -77 16 17.5539 \n\n" \
                     f"MGRS: 18STD9180035700 \n" \
                     f"----------------------------------------------- \n" \
                     f"You will notice there are no ° ' \" symbols \n" \
                     f"There are also no NSEW indications \n\n" \
                     f"Direction is based on positive or negative values \n" \
                     f"Units are separated with a space \n\n" \
                     f"MGRS may contain spaces, they will be stripped \n\n" \
                     f"Degrees may contain leading 0 (-077) but it isn't required \n\n" \
                     f"If there is an error the inputs will display red \n" \
                     f"Tags are just a reference for the text output \n\n" \
                     f"This information is for general reference only \n"

        ok = QtWidgets.QMessageBox.information(self, "Help", formatInfo, QtWidgets.QMessageBox.Yes)




app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()