import camelot
from camelot.core import TableList

# This script reads the Rudolph_Punkttabelle_[year].pdf file and extracts the tables
# Data is structurally stored in CSV files named: ./rudolph_tables-page-[1 - 24]-table-1.csv
# To get data from the CSV file, use the ReadCSV class in the ../Src/RudolphTable.py file
# You can find the rudolph tables on https://www.swimstats.net/rudolphtables

PDF = "Rudolph_Punkttabelle_2025.pdf"

content: TableList = camelot.read_pdf(PDF, "all")

content.export("rudolph_tables.csv", "csv")