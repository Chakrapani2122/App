# 🌱 Soil Microbial Agroecology Lab (SMAL) – Web Application

## Kansas State University

The **Soil Microbial Agroecology Lab (SMAL)** at Kansas State University is dedicated to advancing soil health through comprehensive research on water efficiency, nutrient and energy balance, and climate change. This repository contains the **SMAL Lab Data Management & Visualization Web Application**, built with **Streamlit**.

---

## 📑 Table of Contents

1. [Overview](#-overview)
2. [Technology Stack](#-technology-stack)
3. [Project Structure](#-project-structure)
4. [Installation & Setup](#-installation--setup)
5. [Running the Application](#-running-the-application)
6. [Application Architecture](#-application-architecture)
7. [Page-by-Page Documentation](#-page-by-page-documentation)
   - [Home Page](#1--home-page)
   - [Upload Page](#2--upload-page)
   - [View Data Page](#3--view-data-page)
   - [Data Schedule Page](#4--data-schedule-page)
   - [Visualizations Page](#5--visualizations-page)
   - [Contact Page](#6--contact-page)
8. [Authentication & Security](#-authentication--security)
9. [Data Storage & GitHub Integration](#-data-storage--github-integration)
10. [Dependencies](#-dependencies)
11. [About the Lab](#-about-the-lab)
12. [License](#-license)

---

## 🔎 Overview

This web application serves as a centralized data management and visualization platform for the SMAL research lab. It allows researchers and lab members to:

- **Upload** research data files (CSV, Excel, text, images) to a centralized GitHub repository.
- **View** and explore uploaded datasets with data previews, column data type inspection, missing value analysis, and descriptive statistics.
- **Schedule** and track research team data assignments via a data schedule table.
- **Visualize** data through a gallery of previously saved visualizations and a custom visualization builder supporting 11 plot types.
- **Access** lab contact information and resources.

The application uses **GitHub** as its backend data store, interacting with the GitHub API to read, write, and organize research data files within a structured repository (`Chakrapani2122/Data`).

---

## 🛠 Technology Stack

| Component | Technology |
|-|-|
| **Frontend / UI Framework** | [Streamlit](https://streamlit.io/) v1.24.1 |
| **Programming Language** | Python 3 |
| **Data Manipulation** | [Pandas](https://pandas.pydata.org/) v2.1.1 |
| **Data Visualization** | [Matplotlib](https://matplotlib.org/) v3.7.3, [Seaborn](https://seaborn.pydata.org/) v0.12.2 |
| **Image Handling** | [Pillow (PIL)](https://python-pillow.org/) v9.5.0 |
| **Excel Support** | [openpyxl](https://openpyxl.readthedocs.io/) v3.1.2 |
| **HTTP / API Client** | [Requests](https://docs.python-requests.org/) v2.31.0 |
| **Numerical Computing** | [NumPy](https://numpy.org/) v1.26.0 |
| **Scientific Computing** | [SciPy](https://scipy.org/) v1.11.3 |
| **Backend Data Storage** | GitHub Repository (via GitHub REST API) |
| **Metadata Format** | XML (for visualization descriptions) |

---

## 📁 Project Structure

```
App/
├── app.py                    # Main entry point – Streamlit app with sidebar navigation
├── upload.py                 # Upload page – file upload and GitHub push logic
├── view_data.py              # View Data page – browse and inspect repository data
├── data_schedule.py          # Data Schedule page – displays research team schedule
├── visualizations.py         # Visualizations Gallery page – view saved visualizations
├── custom_visualizations.py  # Custom Visualizations page – interactive plot builder
├── contact.py                # Contact page – lab contact information
├── requirements.txt          # Python dependency list
├── research_team_data.xlsx   # Local Excel file for the data schedule table
├── LICENSE                   # License file
├── README.md                 # This documentation file
├── assets/
│   ├── logo.png              # SMAL Lab logo (used in sidebar and home page)
│   └── home.png              # Home page banner image
└── __pycache__/              # Python bytecode cache (auto-generated)
```

---

## ⚙ Installation & Setup

### Prerequisites

- **Python 3.8+** installed on your system.
- **pip** (Python package manager).
- A **GitHub Personal Access Token (PAT)** with read/write access to the `Chakrapani2122/Data` repository (for Upload, View Data, and Visualizations features).

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/App.git
   cd App
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure the `assets/` folder contains:**
   - `logo.png` – The SMAL Lab logo
   - `home.png` – The home page banner image

5. **Ensure `research_team_data.xlsx`** is present in the root directory (used by the Data Schedule page).

---

## 🚀 Running the Application

Start the Streamlit application by running:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`. The page is configured with:
- **Page Title:** "Kansas State University - SMAL Lab"
- **Page Icon:** `assets/logo.png`
- **Layout:** Wide mode

---

## 🏗 Application Architecture

### High-Level Design

The application follows a **modular, page-based architecture** using Streamlit's sidebar navigation. Each page is implemented as a separate Python module with a dedicated `show_*_page()` function that the main `app.py` calls based on the selected navigation option.

```
┌─────────────────────────────────────────────────────────────────┐
│                         app.py (Entry Point)                    │
│  ┌───────────┐                                                  │
│  │  Sidebar   │──── Navigation Radio Button                     │
│  │  - Logo    │     ┌──────────────────────────────────────┐    │
│  │  - Title   │     │ Home        → Inline in app.py       │    │
│  │  - Nav     │     │ Upload      → upload.py              │    │
│  └───────────┘     │ View Data   → view_data.py           │    │
│                     │ Data Sched. → data_schedule.py       │    │
│                     │ Visualize   → visualizations.py      │    │
│                     │              + custom_visualizations  │    │
│                     │ Contact     → contact.py             │    │
│                     └──────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │   GitHub REST API (Backend)    │
              │   Repo: Chakrapani2122/Data    │
              │   ┌─────────────────────────┐ │
              │   │ Research Area 1/         │ │
              │   │   ├── Data Folder A/    │ │
              │   │   │   ├── file.csv      │ │
              │   │   │   └── file.xlsx     │ │
              │   │   └── Data Folder B/    │ │
              │   │ Research Area 2/         │ │
              │   │ visualizations/          │ │
              │   │   ├── plot1.png         │ │
              │   │   └── descriptions.xml  │ │
              │   └─────────────────────────┘ │
              └───────────────────────────────┘
```

### Navigation Flow

1. **`app.py`** initializes the Streamlit page configuration, loads the logo, and renders the sidebar.
2. A **sidebar radio button** offers six navigation options: Home, Upload, View Data, Data Schedule, Visualizations, and Contact.
3. Based on the user's selection, the corresponding page module function is invoked.
4. Pages that require data access (Upload, View Data, Visualizations, Custom Visualizations) authenticate via a **GitHub Personal Access Token** (stored in `st.session_state['github_token']` for session persistence).

### Session State Management

The application uses Streamlit's `st.session_state` to persist data across reruns:

| Key | Purpose |
|-|-|
| `github_token` | Stores the validated GitHub PAT for the duration of the session, shared across all pages |
| `plot_image` | Stores the generated plot image buffer in the Custom Visualizations page |

### Caching Strategy

Several functions use **`@st.cache_data(ttl=300)`** (5-minute TTL) to cache GitHub API responses, reducing redundant network calls and improving performance:
- `get_repo_contents()` in `upload.py`, `view_data.py`, and `custom_visualizations.py`
- `fetch_visualizations()` in `visualizations.py`
- `fetch_description()` in `visualizations.py`

---

## 📄 Page-by-Page Documentation

### 1. 🏠 Home Page

**File:** `app.py` (inline)

**Purpose:** Provides an introduction to the Soil Microbial Agroecology Lab, its vision, research focus, and leadership.

**Flow:**
1. Displays the SMAL Lab logo and a welcome title in a two-column layout.
2. Shows the home page banner image (`assets/home.png`).
3. Renders rich Markdown content covering:
   - Lab vision and mission
   - Research focus areas (Microbial Ecology, Soil Health Indicators, Rhizosphere Microbes)
   - Detailed research areas
   - Leadership information about Dr. Charles (Chuck) Rice

**No authentication required.**

---

### 2. 📎 Upload Page

**File:** `upload.py` → `show_upload_page()`

**Purpose:** Allows researchers to upload data files to the GitHub repository, organized by research area and data folder.

**Supported File Types:** `.xlsx`, `.csv`, `.txt`, `.dat`, `.jpg`, `.png`

**Flow:**

1. **Authentication:**
   - Checks for an existing GitHub token in `st.session_state['github_token']`.
   - If none is found, prompts the user to enter a security token (password-masked input).
   - Validates the token by making a test API call to the GitHub repository.
   - On success, stores the token in session state and displays a success message.

2. **File Upload:**
   - Provides a multi-file uploader accepting the supported file types.
   - Detects and warns about duplicate file names.

3. **File Preview:**
   - Users select a file from the uploaded batch to preview.
   - **Excel files (`.xlsx`):** Allows sheet selection and displays the first 100 rows as a DataFrame.
   - **CSV files:** Displays the first 100 rows as a DataFrame.
   - **Text/DAT files:** Displays the raw text content in a text area.
   - **Image files (`.jpg`, `.png`):** Renders the image inline.
   - For tabular data (Excel/CSV), an expandable section shows **column data types** organized in a two-column table layout.

4. **Destination Selection:**
   - Fetches the repository's top-level directory listing (research areas) via the GitHub API.
   - The user selects a **Research Area** (top-level directory) from a dropdown.
   - Based on the selection, fetches subdirectories and prompts for a **Research Data Folder**.

5. **Upload Execution:**
   - On clicking the "Upload" button, each file is uploaded individually to the selected path (`<ResearchArea>/<DataFolder>/<FileName>`) via a `PUT` request to the GitHub Contents API.
   - Checks for pre-existing files (HTTP 409) and reports per-file status (success, already exists, or error).

**Key Functions:**
- `upload_to_github(file, path, token)` – Encodes file content as Base64 and uploads via GitHub API.
- `get_repo_contents(token, path)` – Fetches directory listings from GitHub (cached for 5 minutes).
- `show_column_data_types(df)` – Renders column names and data types in an expandable two-column table.

---

### 3. 📊 View Data Page

**File:** `view_data.py` → `show_view_data_page()`

**Purpose:** Browse and inspect data files stored in the GitHub repository, with data previews, column analysis, and descriptive statistics.

**Supported File Types for Preview:** `.xlsx`, `.csv`, `.txt`, `.md`, `.jpg`, `.jpeg`, `.png`

**Flow:**

1. **Authentication:**
   - Same token flow as the Upload page – checks session state first, then prompts if needed.
   - Validates the token using `validate_token()`.

2. **Hierarchical Navigation:**
   - Three cascading dropdown selectors in a three-column layout:
     - **Research Area** – top-level directories from the repository.
     - **Research Data Folder** – subdirectories within the selected research area.
     - **File** – files within the selected folder (filtered to supported types).

3. **File Content Display:**
   - **Excel files:** Provides a sheet selector dropdown, then displays the full DataFrame and column data types.
   - **CSV files:** Displays the full DataFrame and column data types.
   - **Text/Markdown files:** Renders the decoded text content.
   - **Images:** Displays the image inline with a caption.

4. **Data Insights (Expandable Section):**
   - **Shape:** Number of rows and columns.
   - **Missing Values:** Lists columns with missing values count, displayed across four columns. Shows "no missing values" if the data is complete.
   - **Descriptive Analysis:** Outputs `df.describe()` as an interactive DataFrame (count, mean, std, min, 25%, 50%, 75%, max for numeric columns).

**Key Functions:**
- `validate_token(token)` – Quick validation of the GitHub PAT.
- `get_repo_contents(token, path)` – Cached repository browsing.
- `display_file_content(token, path)` – Downloads and renders file content based on file extension.
- `show_column_data_types(df)` – Column data type inspector.

---

### 4. 📅 Data Schedule Page

**File:** `data_schedule.py` → `show_data_schedule_page()`

**Purpose:** Displays a research team data collection schedule from a local Excel file.

**Flow:**

1. Renders the page title "📅 Data Schedule".
2. Reads the `research_team_data.xlsx` file from the application's root directory using Pandas.
3. Displays the full content as a static Streamlit table (`st.table()`).

**No authentication required.** This page reads from a local file, not the GitHub repository.

---

### 5. 📈 Visualizations Page

**File:** `visualizations.py` → `show_visualizations_page()` and `custom_visualizations.py` → `show_custom_visualizations_page()`

**Purpose:** A two-tab interface combining a visualization gallery and a custom visualization builder.

**Tab Structure (defined in `app.py`):**
- **Gallery tab** – Displays previously saved visualizations from GitHub.
- **Custom tab** – Interactive plot builder for creating new visualizations.

---

#### 5a. Gallery Tab (`visualizations.py`)

**Purpose:** Displays all PNG visualizations stored in the `visualizations/` folder of the GitHub repository along with their descriptions.

**Flow:**

1. **Authentication:**
   - Uses the shared session token or prompts for one.

2. **Fetch Visualizations:**
   - Calls `fetch_visualizations(token)` to list all files in the `visualizations/` directory.
   - Calls `fetch_description(token)` to download and parse `visualizations/descriptions.xml`.

3. **Description Parsing:**
   - Parses the XML file to build a dictionary mapping visualization names to their descriptions.
   - XML structure:
     ```xml
     <Visualizations>
       <Visualization>
         <Name>plot_name</Name>
         <Description>A description of the plot</Description>
       </Visualization>
     </Visualizations>
     ```

4. **Gallery Rendering:**
   - Iterates over all `.png` files in the visualizations folder.
   - For each image, displays a two-column layout:
     - **Left column:** The visualization image.
     - **Right column:** The name and description (or "No description available" if not found in the XML).

**Key Functions:**
- `fetch_visualizations(token)` – Cached listing of the visualizations directory.
- `fetch_description(token)` – Cached download and decode of `descriptions.xml`.

---

#### 5b. Custom Tab (`custom_visualizations.py`)

**Purpose:** An interactive data visualization builder that allows researchers to create plots from repository or uploaded data and save them to the GitHub repository.

**Supported Plot Types (11):**
1. Scatter Plot
2. Line Plot
3. Bar Plot
4. Histogram
5. Box Plot
6. Violin Plot
7. Heatmap
8. Pair Plot
9. Regression Plot
10. Density Plot
11. Swarm Plot

**Flow:**

1. **Authentication:**
   - Same shared session token flow.

2. **Data Source Selection:**
   - **"Select from repository"** – Uses three cascading dropdowns (Research Area → Data Folder → File) to load a dataset from GitHub.
   - **"Upload new file"** – Provides a file uploader for CSV or Excel files. For Excel, allows sheet selection.

3. **Data Preview:**
   - Displays the selected dataset in an expandable preview section.
   - Shows column data types in an expandable two-column table.

4. **Plot Configuration (Three-Column Layout):**
   - **X-axis columns:** Multi-select for one or more columns.
   - **Y-axis columns:** Multi-select for one or more columns.
   - **Plot type:** Dropdown selector for one of the 11 plot types.

5. **Plot Generation:**
   - On clicking "Generate Plot", creates a Matplotlib/Seaborn figure (10x6 inches).
   - Applies the selected plot type with the chosen axis columns.
   - Displays the plot inline via `st.pyplot()`.
   - Saves the plot image as a PNG in `st.session_state['plot_image']`.

6. **Save to GitHub:**
   - After generation, displays the plot and provides input fields for:
     - **Visualization name** – used as the filename.
     - **Visualization description** – stored in the XML metadata.
   - On clicking "Save":
     - Uploads the image to `visualizations/<name>.png` in the GitHub repository.
     - Creates or updates `visualizations/descriptions.xml`:
       - If the XML file already exists, downloads it, parses it, appends the new `<Visualization>` element, and re-uploads.
       - If the XML file does not exist, creates a new XML document with the visualization entry.
     - Validates the XML before uploading using `validate_xml()`.
     - Reports success or failure.

**Key Functions:**
- `upload_to_github(file_content, path, token, message, sha)` – Uploads content to GitHub with optional SHA for updates.
- `get_file_sha(path, token)` – Retrieves the SHA hash of an existing file (required for updating files via the GitHub API).
- `validate_xml(xml_content)` – Validates XML well-formedness.
- `display_file_content(token, path)` – Downloads and parses CSV/Excel files from GitHub.

---

### 6. 📞 Contact Page

**File:** `contact.py` → `show_contact_page()`

**Purpose:** Displays the SMAL Lab contact information.

**Content:**
- **Address:** 2004 Throckmorton PSC, 1712 Claflin Road, Manhattan, KS 66506-0110
- **Phone:** +1 (785) 532-6101
- **Email:** agronomy@k-state.edu
- **Website:** [ksusoilmicrobes.com](https://www.ksusoilmicrobes.com/)

**No authentication required.**

---

## 🔐 Authentication & Security

### GitHub Personal Access Token (PAT)

The application uses **GitHub Personal Access Tokens** to authenticate against the GitHub REST API. Tokens are required for:
- Uploading files (write access)
- Viewing repository data (read access)
- Browsing and saving visualizations (read/write access)

### Token Flow

1. When a user navigates to a page requiring authentication, the app first checks `st.session_state['github_token']`.
2. If no token is stored, a **password-masked text input** prompts the user.
3. The entered token is validated by making a quick `GET` request to `https://api.github.com/repos/Chakrapani2122/Data`.
4. If the validation succeeds (HTTP 200), the token is stored in `st.session_state['github_token']` and reused across all pages for the remainder of the session.
5. If the validation fails, an error message is displayed and the token is not stored.

### Security Considerations

- Tokens are entered via **password-masked input fields** (`type="password"`) and are never displayed to the user.
- Tokens are stored only in Streamlit's **server-side session state** (not exposed to the browser's client-side storage).
- Token validation is performed on every page that requires it, ensuring unauthorized tokens cannot access data.
- The token persists only for the duration of the browser session.

---

## 🗄 Data Storage & GitHub Integration

### Repository Structure

The application uses the GitHub repository **`Chakrapani2122/Data`** as its central data store. The repository is organized hierarchically:

```
Chakrapani2122/Data/
├── <Research Area 1>/
│   ├── <Data Folder A>/
│   │   ├── dataset1.csv
│   │   ├── dataset2.xlsx
│   │   └── ...
│   └── <Data Folder B>/
│       └── ...
├── <Research Area 2>/
│   └── ...
└── visualizations/
    ├── plot1.png
    ├── plot2.png
    └── descriptions.xml
```

### API Interactions

| Operation | HTTP Method | Endpoint | Used In |
|-|-|-|-|
| List directory contents | `GET` | `/repos/{owner}/{repo}/contents/{path}` | Upload, View Data, Custom Viz |
| Download file content | `GET` | `/repos/{owner}/{repo}/contents/{path}` | View Data, Visualizations |
| Upload / Create file | `PUT` | `/repos/{owner}/{repo}/contents/{path}` | Upload, Custom Viz (Save) |
| Validate token | `GET` | `/repos/{owner}/{repo}` | All authenticated pages |

### Visualization Metadata

Visualization descriptions are stored in an XML file (`visualizations/descriptions.xml`) with the following schema:

```xml
<?xml version='1.0' encoding='utf-8'?>
<Visualizations>
  <Visualization>
    <Name>visualization_name</Name>
    <Description>A description of what this visualization shows.</Description>
  </Visualization>
  <!-- Additional entries -->
</Visualizations>
```

This file is created or updated programmatically when users save visualizations from the Custom Visualizations page.

---

## 📦 Dependencies

All dependencies are listed in `requirements.txt`:

| Package | Version | Purpose |
|-|-|-|
| `streamlit` | 1.24.1 | Web application framework |
| `requests` | 2.31.0 | HTTP client for GitHub API calls |
| `pandas` | 2.1.1 | Data manipulation and analysis |
| `openpyxl` | 3.1.2 | Excel file reading/writing support |
| `matplotlib` | 3.7.3 | Plot rendering engine |
| `seaborn` | 0.12.2 | Statistical data visualization |
| `Pillow` | 9.5.0 | Image loading and processing |
| `numpy` | 1.26.0 | Numerical computing |
| `setuptools` | >=68.0.0 | Package build utilities |
| `scipy` | 1.11.3 | Scientific computing |

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🌱 About the Lab

### Vision and Mission

SMAL envisions sustainable agricultural systems that are productive, efficient in water, nutrients, and energy, resilient to climate change, and promote soil health. The lab provides leadership in understanding **soil microbial ecology** in grassland and agricultural systems.

### Research Focus

1. **Microbial Ecology and Processes** – Investigating microbial ecology, carbon (C), and nitrogen (N) processes in grassland and agricultural ecosystems.
2. **Soil Health Indicators** – Identifying biological indicators of soil health and practices that sustain and enhance it.
3. **Rhizosphere Microbes** – Exploring the role and potential of microbes in the rhizosphere to boost plant growth and improve water and nutrient efficiency.

### Research Areas

- Carbon and nitrogen analysis in different land uses
- Carbon and nitrogen mineralization
- Factors affecting soil fungi and bacteria populations
- Mycorrhizae population dynamics
- Effects of tillage, nutrients, and cropping systems on soil microbial populations
- Soil aggregate formation and stability
- Soil water infiltration capability
- Phospholipid fatty acids and neutral lipid fatty acids in soil organic matter
- Soil enzyme activity
- Stable isotope 13C and 15N analysis

### Leadership

The lab is led by **Dr. Charles (Chuck) Rice**, University Distinguished Professor and holder of the Vanier University Professorship at Kansas State University. Dr. Rice is a Professor of Soil Microbiology in the Department of Agronomy, co-winner of the **2007 Nobel Peace Prize** for contributions to the UN's Intergovernmental Panel on Climate Change, and Past President of the Soil Science Society of America.

---

## 📜 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.
