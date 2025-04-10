# 🏊‍♂️ Rudolpher

**Rudolpher** is a Python project that automatically extracts swimming competition results real time from internet (e.g. from [swimrankings.net](https://www.swimrankings.net/)) and compares them with a local Rudolph time limit table stored in csv files. The project is meant to calculate a ranking of rudolph scores of swimmers in a certain club.

---

## 📁 Project Structure

```
Rudolpher/
├── Interface/        # Command-line interface for user interaction
├── RudolphTables/    # Extracts tables from PDF files
├── Database/         # SQLite database stores the swimmer information locally
├── Src/              # Main logic and controller scripts
├── main.py           # Main entry point for the application
```

---

## ⚙️ Requirements

To run this project, you need the following Python packages:

```bash
pip install -r requirements.txt
```

**requirements.txt**
```
camelot-py[cv]
pandas
bs4
beautifulsoup4
requests
PyQt5

```

> `sqlite3` is included with Python by default and does not require separate installation.

You’ll also need a few **system dependencies**:

### ✅ System dependencies (based on your OS)

#### Linux:
```bash
sudo apt install ghostscript python3-tk poppler-utils
```

#### Windows:
1. Install [**Ghostscript**](https://www.ghostscript.com/download/gsdnld.html) and add it to your **PATH**.
2. Install [**Poppler for Windows**](https://github.com/oschwartz10612/poppler-windows/releases) and add the `bin/` folder to your **PATH**.

---

## 📥 PDF File

> ℹ️ **Important:** You must manually download the PDF containing the rudolph scores from a site like [swimstats.net](https://www.swimstats.net/rudolphtables).  
> Make sure it is a **vector-based PDF** (not a scanned image), or the table extraction will fail.

Place the PDF file in the RudolphTables directory in the project root along with the PDFReader script.
In the script itself, you can specify the name of the PDF file you want to process.

---

## 📊 Database
The database is created automatically when you run the program for the first time. It will be stored in the `Database/` directory.

## 🚀 Usage

1. **Read and process the PDF:**

```bash
cd RudolphTables
python3 pdf_reader.py 
```

2. **Run the comparison logic:**

Depending on how you want to run the logic:

```bash
python main.py
```
---

## 🧠 What does Rudolpher do?

- The GUI allows you to add/remove swimmers and their information from the database.
- The GUI also shows the ranking of boys/girls of a specific swimming club based on teh rudolph scores.
- If no rudolph scores are available, the swimmers are ordered based on their name.
- You can only add people from the swimming club specified in the Src/HTMLParser.py - get_athlete_info function.
- By double-clicking on a swimmer in the table, you can refresh the rudolph score information.
- Swimming results are parsed from https://swimrankings.net by visiting a swimmer's unique website (based on unique swimrankings ID stored in the database).
- Compares them to predefined time limits in the local CSV files generated from the PDF.
---

## Extra notes
- To calculate the scores, I used linear interpolation of the time limits.
- The GUI and error messages are in Dutch.

## 📝 Further Improvements
- To refresh user information (such as age), user has to be deleted from the database and re-added.
- The program will only calculate the rudolph scores in the right way in the second half (from january so on) of the season.

---

## 👨‍💻 Author

- Emir  
  Computer Science Student

---

## 🐍 Python Version

- Python 3.10 or later is recommended.

---

## 📃 License

MIT License – Feel free to use or modify this project as needed.
