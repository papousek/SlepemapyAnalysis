### About
SlepemapyAnalysis is a Python tool used for data analysis, map and graph visualisations. It uses data obtained from users learning geography through adaptive system available on [Slepemapy](http://www.slepemapy.cz). Each class has specific role:

* Inputoutput is responsible for csv and yaml
* Analysis is used for general calculations on DataFrames, most of the methods return pandas Series objects
* Map is responsible for drawing choropleth maps in .svg format through kartograph. It has separate methods for drawing, legend, title, classification methods etc.
* Graph class is used for drawing graphs

------

### Requirements
All of the requirements are listed in requirements.txt. Some of them (namely [GDAL](https://pypi.python.org/pypi/GDAL/), [kartograph](http://kartograph.org/docs/kartograph.py/)) will probably not install automatically through pip. 

You will also need the geography.answer.csv, [geography.places.csv](../master/geography.places.csv) and [shapefile](../master/ne_110m_admin_1_countries) data for map regions. These shapefiles are available on [Natural Earth Data](http://www.naturalearthdata.com/).

------

### Usage example
There are 3 types of filtering: by user, by place, global. Then there are also 2 types of visualisations - maps and graphs. You can combine those to generate predefined graphs/maps by call from commandline:
python [graphs/maps]-[user/place/global].py -i <id1> <id2> ... <idn>

So for example, if you want to generate graphs for 5 specific users, you can run from commandline:
python graphs-user.py -i 10 25 2277 96 156

Those generators expect you have: geography.answer.csv, [geography.places.csv](../master/geography.places.csv), [difficulties.yaml](../master/difficuties.yaml)


### For much more customization and analysis read the [documentation](../master/documentation/html/index.html)