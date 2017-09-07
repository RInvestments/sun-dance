# GNUMERIC Plugin.

This plugin provides for user defined functions in gnumeric (a spreadsheet program from GNU). 
Python can be used to define these functions. Essentially this provides hook to call
python functions from gnumeric spreadsheet. My python functions than connect to 
the flask-site (stock api) via http to retrive requested stock data. 

## Files
- plugin.xml : List of user defined functions 
- py_func.py : This file defines each of the custom-functions in python. 


Need to put this folder (possibly its softlink also should be ok!) in:
/home/mpkuse/.gnumeric/1.12.28/plugins/kuse-py-func

## References
This plugin is made from templates and example provided in links below. Note that gnumeric is
an extremely buggy program. I am using it just because it is very straight forward to write
plugins for it. 

https://help.gnome.org/users/gnumeric/stable/sect-extending-python.html.en

http://www.bruunisejs.dk/PythonHacks/rstFiles/500%20Notes%20on%20spreadsheets%20etc.html
