# SBOM Security Analysis for Key Node.js Libraries

This project analyzes the **risk of key Node.js libraries** by combining **SBOM (CycloneDX)** reports with **OSV vulnerability scans**. Using **Pandas** for data wrangling and **Bokeh** for interactive visualizations, we identify the **most at-risk libraries in OSS projects**.

---

## 📂 Project Structure

```
.
├── index.html                      # Interactive graphs and dashboards
├── key-npm-projects.txt            # Key projects and their metadata
├── README.md                       # Project documentation
├── SBOM & OSV Report Dataset       # Processed datasets (CSV format)
│   ├── all_libraries.csv
│   ├── axios.libraries.csv
│   ├── axios.vuln.csv
│   ├── bcrypt.libraries.csv
│   ├── bcrypt.vuln.csv
│   ├── chalk.libraries.csv
│   ├── chalk.vuln.csv
│   ├── dotenv.libraries.csv
│   ├── dotenv.vuln.csv
│   ├── jest.libraries.csv
│   ├── jest.vuln.csv
│   ├── lodash.libraries.csv
│   ├── lodash.vuln.csv
│   ├── mongoose.libraries.csv
│   ├── mongoose.vuln.csv
│   ├── npm_version_check_results.csv
│   ├── passport.libraries.csv
│   ├── passport.vuln.csv
│   ├── socketio.libraries.csv
│   ├── socketio.vuln.csv
│   ├── tailwindcss.libraries.csv
│   └── tailwindcss.vuln.csv
├── SBOM-Security-Analysis.ipynb    # Jupyter Notebook with Pandas + Bokeh analysis
└── SBOMs & OSV Report Raw          # Raw SBOMs and OSV reports
    ├── axios
    ├── bcrypt
    ├── chalk
    ├── cyclonedx_to_csv.py         # Convert CycloneDX SBOM to CSV
    ├── dotenv
    ├── jest
    ├── lodash
    ├── mongoose
    ├── osv_to_csv.py               # Convert OSV JSON reports to CSV
    ├── passport
    ├── socketio
    └── tailwindcss
```

---

## 📊 Data Sources

- **SBOM Reports (CycloneDX)** → Dependency inventories for each library.
- **OSV Vulnerability Reports** → Security issues identified by osv-scanner.
- **Key Project List** (`key-npm-projects.txt`) → Includes `project_name` and `weekly_downloads`.

Example:
```
project_name, weekly_downloads
axios, 66,960,832
bcrypt, 2,691,666
```

---

## ⚙️ How to Run

### 1️⃣ Install Dependencies
```bash
npm install
npm install -g @cyclonedx/cyclonedx-npm
brew install osv-scanner
```

### 2️⃣ Generate SBOMs (CycloneDX)
```bash
cyclonedx-npm --output-file <library>.cdx.json --output-format json
```

### 3️⃣ Run Vulnerability Scan (OSV)
```bash
osv-scanner -L=./<library>.cdx.json --format=json > <library>.osv.json
osv-scanner -L=./<library>.cdx.json --format=table > <library>.osv.txt
```

### 4️⃣ Convert Reports to CSV
```bash
python cyclonedx_to_csv.py mongoose.cdx.json output.csv
python osv_to_csv.py <library>.osv.json <library>.vul.csv
```

### 5️⃣ Analyze with Pandas + Bokeh
Open the Jupyter notebook:
```bash
jupyter notebook SBOM-Security-Analysis.ipynb
```

Or use **Google Colab** for cloud execution.

---

## 📈 Output

- `index.html` → Interactive graphs (Bokeh)
- `SBOM & OSV Report Dataset` → Processed CSV datasets for all libraries
- Visualizations highlight:
  - Number of vulnerabilities per library
  - Most risky dependencies in OSS projects
  - Download popularity vs. vulnerability exposure

---

## 🚀 Goal

The goal of this project is to **identify the most at-risk Node.js libraries** in open-source projects by combining **SBOM and vulnerability data**.

---


