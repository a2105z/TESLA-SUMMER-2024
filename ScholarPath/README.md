# ScholarPath

**ScholarPath** is a desktop application built with Python and Tkinter to help high school students organize, track, and reflect on their academic journey.  

It provides an easy way to log achievements, scores, experiences, and goals — all stored locally — and export them when needed (for college applications, personal growth tracking, or sharing with mentors).

---

## ✨ Features

- 👤 **User profiles**  
  Create and manage multiple users. Each student has their own categories and entries.

- 📂 **Categories included**
  - Awards & Honors  
  - Professional Experiences  
  - Summer Programs  
  - SAT/ACT/SATII/ACTII Scores  
  - AP Scores  
  - GPA  
  - Future Plans & Competitions  
  - Personal Goals  
  - Reflection Journal  

- ➕ **Add Entries**  
  Add dated entries for each category (MM/DD/YYYY). AP scores support both exam name and score entry.

- 👀 **View & Search Entries**  
  View all logged entries per category, with search functionality to quickly find items.

- ❌ **Delete Entries**  
  Easily remove entries that are no longer relevant.

- 📤 **Export Data**  
  Export a user’s entire data set into a structured CSV file for backup or sharing.

- 🗂 **Persistent Storage**  
  All data is saved locally in `tracker_data.json` and automatically loaded on app start.

---

## 🛠️ Installation & Setup

### Requirements
- Python 3.8+
- Tkinter (comes preinstalled with most Python distributions)

### Clone the repository
```bash
git clone https://github.com/yourusername/ScholarPath.git
cd ScholarPath
````

### Run the app

```bash
python scholarpath.py
```

*(Replace `scholarpath.py` with the filename where your main code lives if you renamed it.)*

---

## 🚀 Usage

1. **Login / Create User**

   * Enter a username and click **Login**.
   * If the username doesn’t exist, you’ll be prompted to create a new user.

2. **Select Category**

   * Choose one of the categories (e.g., *Awards & Honors*).

3. **Add Entries**

   * Click **Add Entry**, provide the date (MM/DD/YYYY), and details.
   * For AP Scores, you’ll be asked for exam name and score.

4. **View / Delete / Search Entries**

   * Use the buttons to view, remove, or search entries in the selected category.

5. **Export Data**

   * Click **Export Data** to save all entries for the user into a `.csv` file.

6. **Logout**

   * Clears the current session and lets you log in as another user.

---

## 💾 Data Storage

* Data is stored in a local JSON file:

  ```
  tracker_data.json
  ```
* Structure per user:

  ```json
  {
    "username": {
      "Awards & Honors": ["MM/DD/YYYY: description", "..."],
      "Professional Experiences": [],
      "AP Scores": ["05/12/2023: AP Biology - 5"],
      "Reflection Journal": []
    }
  }
  ```

---

## 🧪 Future Improvements

* GPA calculator with graphs
* Support for importing/exporting JSON as well as CSV
* Progress analytics (charts for achievements over time)
* Password-protected user accounts
* Cloud sync or backup option

---

## 📜 License

MIT License — free to use, modify, and share.

---

## 👩‍💻 Author

Built with ❤️ to help students document their high school journey and prepare for future opportunities.

```