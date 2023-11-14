# -*- coding: utf-8 -*-
"""
sqliteextract.ipynb

Automatically generated by Colaboratory.
Original file is located at:
    https://colab.research.google.com/drive/1E3fDAQrcYMFoSG1EpWOKoksfAVpdZ0aN

Modified by Enzo Cocca on 2022-02-23
Changes made:
    - User interface modifications
    - Conversion to vector formats

License: CC-BY (Creative Commons Attribution)

This Python code is a method of a class that extracts data from an SQLite database and saves
it as GeoPackage and Shapefile formats.
The data could be filtered to only include records containing a keyword of contractor field.
The method follows these steps:
1- Fetches user-selected paths for the database and Excel file.
2- Checks if the paths are provided, otherwise it prompts the user.
3- Connects to the SQLite database and fetches data from the 'Surveys' table.
4- Filters out records containing the keyword 'Chronicle' and saves them to a temporary JSON file.
5- Reads the data from the JSON file and organizes it into a dictionary.
6- Iterates over the dictionary keys to process each layer of data.
7- For each layer, it creates a DataFrame and converts it to a GeoDataFrame.
8- If the GeoDataFrame has a 'geometry' column, it saves it as a GeoPackage file and a Shapefile.
9- If any error occurs during the process, it catches the exception and prints the traceback.
10- Finally, it closes the SQLite connection and opens the directory containing the saved files.
"""

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QComboBox,
    QLabel,
    QFileDialog,
)
import sys, os
import sqlite3
import json
import pandas as pd
from shapely.geometry import Point, Polygon
import geopandas as gpd
import traceback
import subprocess
import platform


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a vertical box layout
        vbox = QVBoxLayout()

        # Create buttons for database operations
        self.load_db_btn = QPushButton("Load Database sqlite ", self)
        self.load_db_btn.clicked.connect(self.load_db)

        self.save_db_btn = QPushButton("Save Layer", self)
        self.save_db_btn.clicked.connect(self.save_excel)

        self.run_btn = QPushButton("Start Saving", self)
        self.run_btn.clicked.connect(self.on_button_click)

        # Create a read-only text edit for logs
        self.te = QTextEdit()
        self.te.setReadOnly(True)

        # Create line edits for showing file paths
        self.db_path_le = QLineEdit()
        self.db_path_le.setPlaceholderText("Database Path")
        self.db_path_le.setReadOnly(True)

        # Create a combo box for filter keyword selection
        self.filter_keyword_cb = QComboBox(self)
        self.filter_keyword_cb.setEditable(True)  # Make the combo box editable
        self.filter_keyword_cb.addItem("add or choose a filter. If not use no filter")
        self.filter_keyword_cb.setCurrentText("")
        self.filter_keyword_cb.lineEdit().setPlaceholderText(
            "add or choose a filter. If not use no filter"
        )

        self.filter_keyword_cb.addItem(
            "No filter"
        )  # Add 'No filter' as the first option
        # Add other options as needed
        self.filter_keyword_cb.addItem("Chronicle")
        self.filter_keyword_cb.addItem("PaleoWest")

        # Add widgets to the layout
        vbox.addWidget(self.load_db_btn)
        vbox.addWidget(self.save_db_btn)
        vbox.addWidget(self.run_btn)
        vbox.addWidget(QLabel("Database Path:"))
        vbox.addWidget(self.db_path_le)
        vbox.addWidget(QLabel("Filter Keyword by contractor:"))
        vbox.addWidget(self.filter_keyword_cb)
        vbox.addWidget(self.te)

        self.setLayout(vbox)
        self.excel_path_le = QLineEdit(self)
        vbox.addWidget(QLabel("Excel File Path:"))
        vbox.addWidget(self.excel_path_le)

        self.setWindowTitle("Survey123 TO Layer")
        self.setGeometry(300, 600, 600, 600)
        self.show()

    def save_excel(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel File",
            "",
            "Excel Files (*.xlsx);;All Files (*)",
            options=options,
        )
        if filePath:
            self.excel_path_le.setText(filePath)
            self.te.append(f"Excel will be saved to {filePath}")

    def load_db(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "Load SQLite Database",
            "",
            "SQLite Database Files (*.sqlite);;All Files (*)",
            options=options,
        )
        if filePath:
            self.db_path_le.setText(filePath)
            self.te.append(f"Database loaded from {filePath}")

    def run_script(self, filter_keyword=None):
        success = False  # Initialize success to False
        try:
            # Fetch the user-selected paths from the LineEdit widgets
            db_path = self.db_path_le.text()
            # Prendi il percorso completo del file Excel
            excel_path = self.excel_path_le.text()

            # Estrai la directory e il nome base del file Excel
            excel_dir = os.path.dirname(excel_path)
            excel_base_name = os.path.splitext(os.path.basename(excel_path))[0]

            # Costruisci i percorsi per i file GeoPackage e Shapefile
            gpkg_path = os.path.join(excel_dir, f"{excel_base_name}.gpkg")

            # Check if paths are provided
            if not db_path:
                self.te.append("Please load a database first.")
                return

            if not excel_path:
                self.te.append("Please choose a location to save the Excel file first.")
                return

            # Crea la directory se non esiste
            directory = os.path.dirname(gpkg_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Connect to the SQLite database using the user-selected path
            conn = sqlite3.connect(db_path)
            chronicle_records = []

            cursor = conn.cursor()
            cursor.execute("SELECT data FROM Surveys")

            for row in cursor.fetchall():
                json_data = json.loads(row[0])

                # Only append to chronicle_records if filter_keyword is None or found in json_data
                if filter_keyword is None:
                    chronicle_records.append(json_data)
                elif str(filter_keyword) in json.dumps(
                    json_data
                ):  # Convert filter_keyword to string
                    chronicle_records.append(json_data)

            # Save the filtered records to a temporary JSON file
            with open("temp_table1.json", "w", encoding="utf-8") as json_file:
                json.dump(chronicle_records, json_file, indent=2, ensure_ascii=False)

            self.te.append("Data containing 'Chronicle' saved to temp_table1.json")

            # Read the data from the temporary JSON file
            with open("temp_table1.json", "r", encoding="utf-8") as json_file:
                data = json.load(json_file)

            # Initialize an empty dictionary to store the data for each layer
            data_dict = {}

            for item in data:
                # Iterate over all keys in the item
                for key in item.keys():
                    # If the key is not already in the dictionary, add it
                    if key not in data_dict:
                        data_dict[key] = []
                    # Append the data to the list for this key
                    data_dict[key].append(item[key])

            def create_point(x):
                if isinstance(x, dict):
                    return Point(x["x"], x["y"], x["z"])
                else:
                    return None

            # Now you can iterate over the keys in the dictionary to process each layer
            for key in data_dict.keys():
                # Create a DataFrame for this layer
                df = pd.DataFrame(data_dict[key])

                # Initialize an empty GeoDataFrame
                gdf = gpd.GeoDataFrame()

                # Check if the DataFrame is not empty
                if not df.empty:
                    # Create geometries
                    if "location" in df.columns:
                        df["geometry"] = df["location"].apply(
                            lambda x: Polygon(x["rings"][0])
                        )
                    elif "point" in df.columns:
                        df["geometry"] = df["point"].apply(create_point)

                    # Convert the DataFrame to a GeoDataFrame
                    gdf = gpd.GeoDataFrame(df, geometry="geometry")
                    gdf.crs = "EPSG:4326"
                else:
                    self.te.append(f"{key} DataFrame is empty, skipping...")

                # Save the GeoDataFrame to a GeoPackage file
                if "geometry" in gdf.columns:
                    # Convert all lists to strings
                    for column in gdf.columns:
                        if (
                            column != "geometry"
                            and gdf[column].apply(type).eq(list).any()
                        ):
                            gdf[column] = gdf[column].astype(str)

                    # Write to the GeoPackage file
                    gdf.to_file(gpkg_path, layer=key, driver="GPKG")
                    self.te.append(f"{key} GEOPACKAGE saved!")
                else:
                    self.te.append(
                        f"{key} GeoDataFrame does not have a geometry column, skipping..."
                    )

                # Save the GeoDataFrame to a Shapefile
                if "geometry" in gdf.columns:
                    shp_path = os.path.join(excel_dir, f"{excel_base_name}_{key}.shp")
                    gdf.to_file(shp_path, driver="ESRI Shapefile")
                    self.te.append(f"{key} ESRI shape file saved!")
                else:
                    self.te.append(
                        f"{key} GeoDataFrame does not have a geometry column, skipping..."
                    )
            # If all processes are successful, set success to True
            success = True
        except Exception:
            self.te.append("An unexpected error occurred:")

            self.te.append(traceback.format_exc())

        finally:
            # Chiusura della connessione SQLite se esiste
            if "conn" in locals():
                conn.close()

            # If all processes were successful, open the directory
            if success:
                if platform.system() == "Windows":
                    subprocess.Popen(f'explorer "{os.path.realpath(excel_dir)}"')
                elif platform.system() == "Darwin":
                    subprocess.Popen(f'open "{os.path.realpath(excel_dir)}"')
                else:
                    subprocess.Popen(f'xdg-open "{os.path.realpath(excel_dir)}"')

    def on_button_click(self):
        # If the current index of the combo box is 0, print a message and return
        if self.filter_keyword_cb.currentIndex() == 0:
            self.te.append("Please choose a filter.")
            return

        # Get the current text of the combo box
        filter_keyword = self.filter_keyword_cb.currentText()

        # If the field is empty or set to 'None', set filter_keyword to None
        if not filter_keyword or filter_keyword == "No filter":
            filter_keyword = None

        # Run the script with the specified filter keyword
        self.run_script(filter_keyword)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
