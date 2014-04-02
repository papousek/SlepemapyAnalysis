mapViz is a Python tool for data analysis (with pandas), map drawing (through kartograph) and graph drawing (with matplotlib) specifically for user data obtained from interactive geography system called slepemapy.cz

All of the requirements are listed in requirements.txt. Some of them (namely GDAL, kartograph) will probably not install automatically through pip. 


This module consists of multiple classes:
-Importer is responsible for loading and parsing csv into pandas DataFrame
-Analysis is used for general calculations on DataFrames, most of the methods return pandas Series objects
-Map is responsible for drawing choropleth maps in .svg format through kartograph. It has separate methods for drawing, legend, title, classification methods etc.
-Graph class is used for drawing graphs

There is an example main included to show prepared graphs and maps. 