# Survey123 to Layer Converter

This application provides a graphical user interface (GUI) for converting data from a SQLite database into GeoPackage and Shapefile formats, with optional filtering by keywords. It is built using PyQt5 and integrates with geospatial libraries to handle the conversion process.

## Features

- Load a SQLite database and select it for processing.
- Save the output as an Excel file, GeoPackage, or Shapefile.
- Filter records by a specified keyword.
- View logs of the operations within the GUI.

## Requirements

To run this application, you need the following Python packages installed:
- PyQt5
- sqlite3 (included in the standard library)
- json (included in the standard library)
- pandas
- Shapely
- GeoPandas

## Installation

Ensure you have Python installed on your system, then install the required packages using pip:


## Usage

1. Run the script to launch the GUI.
2. Click "Load Database sqlite" to load the SQLite database file.
3. Click "Save Layer" to specify the path where the Excel file will be saved.
4. Choose a filter from the dropdown or add a new one if needed.
5. Click "Start Saving" to begin the conversion process.
6. Monitor the progress and any messages in the text edit area of the GUI.

## Notes

- The application uses a temporary JSON file (`temp_table1.json`) to store intermediate data during processing.
- The application can open the directory containing the saved files using the default file explorer for the system after successful processing.

## License

This project is open-source and available under GPL-3.0.
