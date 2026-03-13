# SMAL Lab Web Application — Complete Technical Documentation

> **Kansas State University — Soil Microbial Agroecology Lab (SMAL)**  
> Last updated: March 2026  
> Application framework: [Streamlit](https://streamlit.io/)  
> Backend data store: GitHub Repository (`Chakrapani2122/Data`)

---

## Table of Contents

1. [Application Overview](#1-application-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Installation & Local Setup](#4-installation--local-setup)
5. [Running the Application](#5-running-the-application)
6. [Architecture & Data Flow](#6-architecture--data-flow)
7. [Authentication & Security Token](#7-authentication--security-token)
8. [File-by-File Code Reference](#8-file-by-file-code-reference)
   - [app.py — Main Entry Point](#81-apppy--main-entry-point)
   - [github_utils.py — GitHub API Layer](#82-github_utilspy--github-api-layer)
   - [upload.py — Upload Page](#83-uploadpy--upload-page)
   - [view_data.py — View Data Page](#84-view_datapy--view-data-page)
   - [data_schedule.py — Data Schedule Page](#85-data_schedulepy--data-schedule-page)
   - [visualizations.py — Visualizations Gallery](#86-visualizationspy--visualizations-gallery)
   - [custom_visualizations.py — Custom Plot Builder](#87-custom_visualizationspy--custom-plot-builder)
   - [contact.py — Contact Page](#88-contactpy--contact-page)
9. [Page-by-Page User Guide](#9-page-by-page-user-guide)
   - [Home](#91-home-page)
   - [Upload](#92-upload-page)
   - [View Data](#93-view-data-page)
   - [Data Schedule](#94-data-schedule-page)
   - [Visualizations — Gallery Tab](#95-visualizations--gallery-tab)
   - [Visualizations — Custom Tab](#96-visualizations--custom-tab)
   - [Contact](#97-contact-page)
10. [GitHub Repository Structure (Data Repo)](#10-github-repository-structure-data-repo)
11. [Streamlit Session State Reference](#11-streamlit-session-state-reference)
12. [Data Transformation Pipeline](#12-data-transformation-pipeline)
13. [Statistical Test Toolkit](#13-statistical-test-toolkit)
14. [Supported File Types](#14-supported-file-types)
15. [Dependencies & Versions](#15-dependencies--versions)
16. [Known Limitations & Notes for Future Maintainers](#16-known-limitations--notes-for-future-maintainers)
17. [About the Lab](#17-about-the-lab)

---

## 1. Application Overview

This is a **Streamlit-based web application** built for the **Soil Microbial Agroecology Lab (SMAL)** at Kansas State University. It serves as a centralized, browser-accessible platform for:

- **Uploading** research data files (CSV, Excel, text, images) directly to a private GitHub repository used as a data store.
- **Browsing and inspecting** repository data files with rich previews, column type inspection, descriptive statistics, and missing value analysis.
- **Transforming data** through a no-code Transformation Pipeline Builder (filter, group-by, normalize, log-transform).
- **Running statistical tests** (t-test, ANOVA, Mann-Whitney U, Chi-square) directly in the browser.
- **Viewing a gallery** of saved chart images stored in the GitHub repository.
- **Creating custom visualizations** from repository files or local uploads using 11 plot types, with optional side-by-side comparison mode.
- **Tracking research data assignments** via a team schedule read from a local Excel file.
- **Accessing lab contact information.**

The application uses **GitHub as its backend** — there is no separate database or server. All persistent data (uploads, visualization images, visualization metadata) lives inside the `Chakrapani2122/Data` GitHub repository. Access is controlled by a **GitHub Personal Access Token (PAT)** entered by the user at runtime.

---

## 2. Technology Stack

| Component | Technology | Version |
|---|---|---|
| Frontend / UI framework | [Streamlit](https://streamlit.io/) | 1.24.1 |
| Programming language | Python | 3.8+ |
| Data manipulation | [Pandas](https://pandas.pydata.org/) | 2.1.1 |
| Data visualization | [Matplotlib](https://matplotlib.org/) | 3.7.3 |
| Data visualization | [Seaborn](https://seaborn.pydata.org/) | 0.12.2 |
| Image handling | [Pillow (PIL)](https://python-pillow.org/) | 9.5.0 |
| Excel support | [openpyxl](https://openpyxl.readthedocs.io/) | 3.1.2 |
| HTTP / GitHub API client | [Requests](https://docs.python-requests.org/) | 2.31.0 |
| Numerical computing | [NumPy](https://numpy.org/) | 1.26.0 |
| Scientific / statistical computing | [SciPy](https://scipy.org/) | 1.11.3 |
| Backend data storage | GitHub REST API v3 | — |
| Visualization metadata format | XML (standard library `xml.etree.ElementTree`) | — |

---

## 3. Project Structure

```
App/
├── app.py                    # Main entry point — Streamlit app with sidebar navigation
├── upload.py                 # Upload page — file upload and GitHub push logic
├── view_data.py              # View Data page — browse, inspect, transform, and analyze files
├── data_schedule.py          # Data Schedule page — displays research team schedule table
├── visualizations.py         # Visualizations Gallery page — view saved PNG visualizations
├── custom_visualizations.py  # Custom Visualizations page — interactive plot builder
├── contact.py                # Contact page — lab contact information
├── github_utils.py           # Shared GitHub API helper functions (used by all pages)
├── requirements.txt          # Python dependency list with pinned versions
├── research_team_data.xlsx   # Local Excel file powering the Data Schedule table
├── LICENSE                   # License file
├── README.md                 # High-level readme (GitHub-facing)
├── Documentation.md          # THIS FILE — complete technical documentation
├── assets/
│   ├── logo.png              # SMAL Lab logo (shown in sidebar and home page header)
│   └── home.png              # Home page banner/hero image
└── __pycache__/              # Python bytecode cache (auto-generated, do not edit)
```

---

## 4. Installation & Local Setup

### Prerequisites

| Requirement | Details |
|---|---|
| Python 3.8 or higher | Ensure `python --version` ≥ 3.8 |
| pip | Comes bundled with Python |
| GitHub Personal Access Token (PAT) | Must have **read and write** access (Contents permission) to the `Chakrapani2122/Data` repository |

### Step-by-Step Setup

**1. Clone the application repository:**

```bash
git clone https://github.com/<your-username>/App.git
cd App
```

**2. (Recommended) Create and activate a virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

**3. Install all dependencies:**

```bash
pip install -r requirements.txt
```

**4. Verify assets are in place:**

Ensure both `assets/logo.png` and `assets/home.png` exist. If the logo is missing, the app will show an error banner but will still run.

**5. Verify the data schedule file:**

`research_team_data.xlsx` must exist in the root `App/` directory. This is the file read by the Data Schedule page.

---

## 5. Running the Application

```bash
streamlit run app.py
```

The application opens at `http://localhost:8501` by default. To run on a specific port:

```bash
streamlit run app.py --server.port 8080
```

To expose the app on a network (e.g., within a lab or university network):

```bash
streamlit run app.py --server.address 0.0.0.0
```

---

## 6. Architecture & Data Flow

```
User Browser
     │
     ▼
[Streamlit Frontend (app.py)]
     │  sidebar navigation selects a page
     ▼
┌─────────────────────────────────────────────────────────┐
│  Page Modules                                           │
│  upload.py  │  view_data.py  │  visualizations.py       │
│  custom_visualizations.py  │  data_schedule.py          │
│  contact.py                                             │
└──────────────────────┬──────────────────────────────────┘
                       │ all API calls go through
                       ▼
              [github_utils.py]
              GitHub REST API v3
                       │
                       ▼
         GitHub Repository: Chakrapani2122/Data
         ├── <folder>/                  ← uploaded data files
         └── visualizations/
             ├── <name>.png             ← saved visualization images
             └── descriptions.xml       ← visualization metadata (name + description)
```

### Key Design Decisions

- **GitHub as a database**: The app has no SQL database, no server, and no file system beyond `assets/` and `research_team_data.xlsx`. All user-generated data lives in the `Chakrapani2122/Data` GitHub repository.
- **Token-based access**: A GitHub PAT is entered by the user at runtime and stored in `st.session_state['github_token']`. It is never written to disk or transmitted outside of GitHub API calls.
- **Client-side caching**: GitHub API calls are wrapped with `@st.cache_data(ttl=300)` — responses are cached for 5 minutes per Streamlit session to reduce API rate-limit usage. Caches are cleared after uploads or saves via `clear_github_caches()`.
- **No external auth system**: There is no login/logout system. The GitHub token acts as the sole credential.

---

## 7. Authentication & Security Token

### What Token Is Needed

A **GitHub Personal Access Token (Classic)** with the following permission:
- `repo` (Full control of private repositories) — needed to read/write files in `Chakrapani2122/Data`.

Or for fine-grained tokens:
- Repository: `Chakrapani2122/Data`
- Permission: **Contents** → Read and Write

### How It Works in the App

1. Pages that require GitHub access check `st.session_state.get('github_token')` first.
2. If no token is present in the session, the page renders a **password-type text input** prompting the user to enter one.
3. The entered token is validated by calling `GET https://api.github.com/repos/Chakrapani2122/Data`. A `200` response confirms validity.
4. On success, the token is stored in `st.session_state['github_token']` and reused across all pages **for the duration of the browser session**.
5. Refreshing the browser tab clears the session, requiring re-entry of the token.

### Pages That Require a Token

| Page | Needs Token |
|---|---|
| Home | No |
| Upload | Yes (for upload; file selection shown before token entry) |
| View Data | Yes |
| Data Schedule | No |
| Visualizations (Gallery) | Yes |
| Visualizations (Custom) | Yes |
| Contact | No |

---

## 8. File-by-File Code Reference

### 8.1 `app.py` — Main Entry Point

**Purpose**: Bootstraps the Streamlit app, defines the sidebar, and routes navigation to the correct page module.

**Key responsibilities:**
- Calls `st.set_page_config(...)` to set browser title, favicon (`assets/logo.png`), and wide layout.
- Loads and validates `assets/logo.png` using `PIL.Image.verify()`. Falls back gracefully if the file is missing or corrupt.
- Renders the sidebar with the SMAL Lab logo (50px width) and a `st.sidebar.radio` for navigation.
- Routes to one of 6 modules based on the selected radio item.
- The **Visualizations** page uses `st.tabs(["Gallery", "Custom"])` — both `show_visualizations_page(None, show_header=True)` and `show_custom_visualizations_page(None, show_header=True)` are called inside their respective tab contexts.

**Navigation options:**

| Radio Label | Module Called |
|---|---|
| Home | Inline content in `app.py` |
| Upload | `upload.show_upload_page()` |
| View Data | `view_data.show_view_data_page()` |
| Data Schedule | `data_schedule.show_data_schedule_page()` |
| Visualizations | `visualizations.show_visualizations_page()` + `custom_visualizations.show_custom_visualizations_page()` in tabs |
| Contact | `contact.show_contact_page()` |

---

### 8.2 `github_utils.py` — GitHub API Layer

**Purpose**: Centralized module for all GitHub REST API interactions. All other page modules import from here.

**Constants:**

| Constant | Value |
|---|---|
| `GITHUB_REPO` | `"Chakrapani2122/Data"` |
| `GITHUB_API_URL` | `"https://api.github.com/repos/Chakrapani2122/Data/contents/"` |
| `REQUEST_TIMEOUT` | `30` (seconds) |
| `VISUALIZATION_METADATA_PATH` | `"visualizations/descriptions.xml"` |

**Public Functions:**

| Function | Description |
|---|---|
| `validate_token(token)` | `GET /repos/{GITHUB_REPO}` — returns `True` if status 200. Cached 5 min. |
| `get_repo_contents(token, path="")` | `GET /contents/{path}` — returns list of items. Cached 5 min. |
| `get_file_metadata(token, path)` | `GET /contents/{path}` — returns file metadata dict. Cached 5 min. |
| `get_file_bytes(token, path)` | Downloads file bytes. Tries `download_url` first, falls back to base64-decoding `content` field. Cached 5 min. |
| `fetch_visualization_descriptions(token)` | Downloads `visualizations/descriptions.xml` raw content. Cached 5 min. |
| `load_visualization_metadata(token)` | Parses the XML and returns a `dict[name → {description, metadata}]`. |
| `get_file_sha(path, token)` | Returns the file's SHA (required for updating existing files via the GitHub API). |
| `upload_bytes_to_github(file_bytes, path, token, message, sha=None)` | `PUT /contents/{path}` to create or update a file. Returns `(status_code, response_json)`. |
| `save_visualization_metadata(token, name, description, metadata_dict=None)` | Reads current `descriptions.xml`, upserts a `<Visualization>` node, and writes back via `upload_bytes_to_github`. |
| `clear_github_caches()` | Calls `.clear()` on all `@st.cache_data` decorated functions to force fresh API calls. |
| `github_headers(token, accept=...)` | Returns a dict suitable for `Authorization` and `Accept` headers. |

**Visualization XML Format (`visualizations/descriptions.xml`):**

```xml
<?xml version='1.0' encoding='utf-8'?>
<Visualizations>
  <Visualization>
    <Name>plot_name_here</Name>
    <Description>Human-readable description</Description>
    <Metadata>
      <AnyKey>AnyValue</AnyKey>
    </Metadata>
  </Visualization>
</Visualizations>
```

---

### 8.3 `upload.py` — Upload Page

**Purpose**: Allows users to upload research data files to a chosen folder within the `Chakrapani2122/Data` repository.

**Key functions:**

| Function | Description |
|---|---|
| `show_upload_page()` | Main page entry point. Handles token prompt, file selection, preview, folder navigation, and upload. |
| `_folder_nav_grid(token, nav_prefix, exclude_root=None)` | Renders a cascading 3-column dropdown folder navigator. Returns the currently selected path. Folders named in `exclude_root` are hidden at the root level (used to hide the `visualizations` folder). |
| `_preview_uploaded_file(uploaded_file, selected_sheet=None)` | Renders an inline preview for the selected file (dataframe for CSV/Excel, text area for TXT/DAT, image for JPG/PNG). |
| `show_column_data_types(df)` | Renders an expander showing each column name and its Pandas dtype in a two-column table. |

**Upload Flow:**

1. User enters a GitHub token (stored in session state).
2. User selects one or more files with `st.file_uploader` (allowed: `.xlsx`, `.csv`, `.txt`, `.dat`, `.jpg`, `.png`).
3. Duplicate file names within the selection are detected and warned about.
4. A file preview is shown for the selected file (first 100 rows for tabular data).
5. User navigates the folder tree (`_folder_nav_grid`) to choose a destination. The `visualizations` folder is excluded from navigation.
6. On clicking **Upload**:
   - Each file path is checked with `get_file_metadata`. If already exists, that file is skipped with a warning.
   - Files are uploaded via `upload_bytes_to_github` with a commit message `"Upload {path}"`.
   - `clear_github_caches()` is called after all uploads to refresh subsequent Browse operations.

---

### 8.4 `view_data.py` — View Data Page

**Purpose**: Browse and inspect files stored in the `Chakrapani2122/Data` repository. Provides data previews, descriptive statistics, a Transformation Pipeline Builder, and a Statistical Test Toolkit.

**Key functions:**

| Function | Description |
|---|---|
| `show_view_data_page()` | Main page entry point. Handles token prompt and renders the file navigator. |
| `display_file_content(token, path)` | Downloads and renders the selected file. Returns a DataFrame for tabular files, `None` for binary/text files. |
| `show_column_data_types(df)` | Expander showing column names and Pandas dtypes split across two columns. |
| `_show_data_insights(df)` | Expander showing row/column count, missing values per column, and `df.describe(include="all")` output. |
| `_render_transformation_pipeline(df, file_path)` | Renders the Pipeline Builder UI and returns the transformed DataFrame. |
| `_apply_pipeline(df, steps)` | Pure function: applies a list of transformation step dicts to a DataFrame and returns the result. |
| `_render_statistical_tests(df, file_path)` | Renders four tabs (t-test, ANOVA, Mann-Whitney, Chi-square) and runs selected tests. |
| `_run_t_test(...)` | Runs Welch's or Student's t-test (Levene test decides). Returns result dict with assumptions. |
| `_run_mann_whitney(...)` | Runs Mann-Whitney U test (non-parametric). |
| `_run_anova(...)` | Runs one-way ANOVA with Shapiro and Levene assumption checks. |
| `_run_chi_square(...)` | Runs chi-square test of independence on two categorical columns. |
| `_coerce_scalar(value, series)` | Helper to cast a filter value to the correct type based on the target column's dtype. |
| `_decode_text_content(file_content)` | Decodes bytes using UTF-8, falls back to latin-1. |
| `_download_raw_file(file_name, file_content, mime)` | Renders a `st.download_button` for any file. |
| `_extract_docx_text(file_content)` | Parses a `.docx` file (ZIP format) using `xml.etree.ElementTree` and extracts plain text. |

**File preview by type:**

| Extension | Rendered As |
|---|---|
| `.xlsx`, `.xls` | Interactive `st.dataframe` with sheet selector. Triggers data insights + pipeline + stats. |
| `.csv` | Interactive `st.dataframe`. Triggers data insights + pipeline + stats. |
| `.txt`, `.md`, `.dat` | Read-only `st.text_area` + download button. |
| `.docx` | Extracted plain text in read-only `st.text_area` + download button. |
| `.jpg`, `.jpeg`, `.png` | `st.image` display + download button. |
| Other | Warning message + download button. |

**Folder Navigation:**
- Uses a cascading dropdown approach: each level shows directories + matching files.
- The `visualizations` folder is hidden at root level to prevent accidental browsing of internal PNG assets.
- Dropdowns reuse `st.session_state` keys (`nav_{path}`) persisted across Streamlit reruns.

---

### 8.5 `data_schedule.py` — Data Schedule Page

**Purpose**: Displays a static research team data assignment schedule read from a local Excel file.

**Function:**

| Function | Description |
|---|---|
| `show_data_schedule_page()` | Reads `research_team_data.xlsx` from the project root, loads it into a DataFrame, and renders it as a `st.table`. |

**Important note for maintainers**: The schedule is stored in `research_team_data.xlsx` locally in the `App/` project directory. To update the schedule, edit this Excel file and redeploy/restart the application. There is **no in-app editing** capability for this page.

---

### 8.6 `visualizations.py` — Visualizations Gallery

**Purpose**: Displays all PNG images saved in the `visualizations/` folder of the `Chakrapani2122/Data` repository, with search, sort, and three view modes.

**Key functions:**

| Function | Description |
|---|---|
| `show_visualizations_page(github_token, show_header)` | Main entry point. Handles token prompt (when `show_header=True`) and renders the gallery. |
| `fetch_visualizations(token)` | Calls `get_repo_contents(token, "visualizations")` and returns all items in the folder. |
| `_sort_visualizations(items, sort_by)` | Sorts the list of viz items by name or file size. |
| `_render_gallery_view(items, token)` | 2-column view with image, description, file size, and download button. |
| `_render_grid_view(items, token)` | Compact 3-column view with image and short caption. |
| `_render_list_view(items, token)` | 3-column horizontal layout (thumbnail | name+description | download button) with dividers. |

**Controls available to users:**

| Control | Options |
|---|---|
| Search box | Filters by name or description (case-insensitive substring match) |
| Sort by | Name A-Z, Name Z-A, File Size Small-Large, File Size Large-Small |
| View mode | Gallery (2-col), Grid (3-col), List |

---

### 8.7 `custom_visualizations.py` — Custom Plot Builder

**Purpose**: Allows users to build and save custom visualizations from data files in the repository or from locally uploaded files.

**Supported plot types (11 total):**

| Plot Type | Required Inputs |
|---|---|
| Scatter Plot | X column, one or more Y columns |
| Line Plot | X column, one or more Y columns |
| Bar Plot | X column, one or more Y columns |
| Histogram | One numeric X column |
| Box Plot | X (categorical) column, one Y column |
| Violin Plot | X (categorical) column, one Y column |
| Swarm Plot | X (categorical) column, one Y column |
| Heatmap | Multiple numeric columns (correlation matrix) |
| Regression Plot | X column, one or more Y columns (with regression line) |
| Density Plot | One numeric X column (KDE) |
| Pair Plot | Multiple numeric columns (pairwise scatter matrix) |

**Key functions:**

| Function | Description |
|---|---|
| `show_custom_visualizations_page(github_token, show_header)` | Main entry point. Orchestrates file selection, plot config, generation, and upload. |
| `_repo_file_nav_grid(token, nav_prefix)` | Cascading folder + file navigator; returns selected file path. Only shows `.xlsx` and `.csv` files. |
| `_load_dataset_from_bytes(file_bytes, file_name, key_prefix)` | Reads CSV or Excel bytes into a DataFrame. Sheet selector shown for Excel. |
| `_render_plot_config(df, key_prefix, comparative_mode)` | Renders plot type and axis selectors. Returns a config dict. |
| `_plot_on_axis(ax, df, config, title)` | Draws a single plot onto a Matplotlib `Axes` object using the config dict. |
| `_generate_plot_figure(df, primary_config, ...)` | Generates a `matplotlib.figure.Figure`. Handles single plots, comparative (side-by-side) mode, and Pair Plot. |
| `show_column_data_types(df)` | Same as in other modules — expander with column dtype table. |

**Plot Generation & Save Flow:**

1. User selects a data source (repository file or local upload).
2. User configures the plot (type, axes, title/label text) in the Visualization Builder section.
3. (Optional) User enables **Comparative Mode** to configure a second side-by-side plot on the same data.
4. Click **Generate Plot** → `_generate_plot_figure()` builds the Matplotlib figure and saves it to `st.session_state["plot_image"]` as PNG bytes.
5. The generated image is displayed inline and a **Download** button appears.
6. User enters a name, description, and "Created by" attribution.
7. Click **Upload Visualization** → the PNG is written to `visualizations/{plot_name}.png` and the `descriptions.xml` is updated with the name and description via `save_visualization_metadata`.
8. `clear_github_caches()` is called so the Gallery page immediately reflects the new visualization.

---

### 8.8 `contact.py` — Contact Page

**Purpose**: Displays static lab contact information.

**Content:**
- Address: 2004 Throckmorton PSC, 1712 Claflin Road, Manhattan, KS 66506-0110
- Phone: +1 (785) 532-6101
- Email: agronomy@k-state.edu
- Website: https://www.ksusoilmicrobes.com/

To update contact details, edit the `show_contact_page()` function in `contact.py`.

---

## 9. Page-by-Page User Guide

### 9.1 Home Page

- No token required.
- Displays the SMAL Lab logo and a full description of the lab's vision, mission, research focus, and leadership (Dr. Charles "Chuck" Rice).
- Contains a hero/banner image loaded from `assets/home.png`.
- Entirely static — no user interaction.

### 9.2 Upload Page

1. Navigate to **Upload** in the sidebar.
2. If you have not entered a token this session, enter your GitHub PAT in the password field.
3. Click **Choose files** and select one or more files (`.xlsx`, `.csv`, `.txt`, `.dat`, `.jpg`, `.png`).
4. A preview of the first selected file is shown (first 100 rows for tabular data).
5. Use the **folder dropdowns** to navigate to the desired destination folder in the repository.
6. Click **Upload**.
7. A status message appears for each file indicating success or failure.

**Notes:**
- Uploading to a path where a file already exists will **skip** that file (no overwrite).
- The `visualizations/` folder is intentionally hidden from the folder navigator.
- Files with duplicate names within the same upload batch will trigger a warning.

### 9.3 View Data Page

1. Navigate to **View Data** in the sidebar.
2. Enter your GitHub PAT if prompted.
3. Use the cascading **folder dropdowns** to navigate the repository. When you select a file, its contents are displayed below.
4. For tabular files (CSV/Excel):
   - Full interactive `st.dataframe` is shown.
   - **Show Column Data Types** expander reveals Pandas dtypes.
   - **Expand to view data insights** shows shape, missing values, and descriptive statistics.
   - **Transformation Pipeline Builder** lets you apply chained transformations.
   - **Statistical Test Toolkit** lets you run hypothesis tests.
5. For text/document files: a read-only text area is shown along with a download button.
6. For image files: the image is displayed inline with a download button.

### 9.4 Data Schedule Page

- Navigate to **Data Schedule** in the sidebar.
- No token required.
- The page renders the contents of `research_team_data.xlsx` as a read-only table.
- To update the schedule: edit `research_team_data.xlsx` and restart the app or redeploy.

### 9.5 Visualizations — Gallery Tab

1. Navigate to **Visualizations** in the sidebar, then select the **Gallery** tab.
2. Enter your GitHub PAT if prompted.
3. All PNG files in the `visualizations/` folder of the repository are shown.
4. Use the **Search** box to filter by name or description.
5. Use the **Sort by** dropdown to reorder results.
6. Use the **View mode** dropdown to switch between Gallery (2-col), Grid (3-col), or List layouts.
7. Click **Download** (or **Download plot**) to save any visualization locally.

### 9.6 Visualizations — Custom Tab

1. Navigate to **Visualizations** in the sidebar, then select the **Custom** tab.
2. Enter your GitHub PAT if prompted.
3. Choose **"Select from repository"** to navigate to a CSV/Excel file in the data repository, or choose **"Upload new file"** to upload a local file for visualization only (not saved to the repo).
4. A **Data Snapshot** expander lets you preview the loaded dataset.
5. Under **Visualization Builder**, select a plot type and configure axes/columns.
6. Optionally enable **Comparative Mode** to display two plots side by side, with optional linked axes.
7. Click **Generate Plot**.
8. The generated plot appears below. Click **Download Generated Plot (PNG)** to save it locally.
9. To save the plot to the repository: enter a name, description, and your name, then click **Upload Visualization**. The plot will appear in the Gallery tab.

### 9.7 Contact Page

- Navigate to **Contact** in the sidebar.
- No token required.
- Displays the lab's mailing address, phone, email, and website link.

---

## 10. GitHub Repository Structure (Data Repo)

The application connects to repository `Chakrapani2122/Data`. Its structure is expected to be:

```
Chakrapani2122/Data (repository root)
│
├── <Research Folder A>/           ← any lab-defined folder structure
│   ├── <SubFolder>/
│   │   └── data_file.csv
│   └── another_file.xlsx
│
├── <Research Folder B>/
│   └── ...
│
└── visualizations/                ← auto-managed by the application
    ├── descriptions.xml           ← auto-generated/updated XML metadata file
    ├── plot_name_1.png            ← saved visualization images
    └── plot_name_2.png
```

**Rules:**
- The folder structure above the `visualizations/` directory is entirely user-defined (via uploads).
- `visualizations/` is created automatically the first time a visualization is uploaded.
- `visualizations/descriptions.xml` is created automatically on the first visualization save. It is an XML file with `<Visualizations>` as the root element.
- The application **never deletes** any file from the repository. Deletion must be done manually via GitHub.

---

## 11. Streamlit Session State Reference

Streamlit's `st.session_state` is used as an in-memory store across reruns within the same browser session. The following keys are used by the application:

| Session State Key | Set By | Used By | Description |
|---|---|---|---|
| `github_token` | Upload, View Data, Visualizations, Custom Viz | All pages | The validated GitHub PAT for the current session |
| `plot_image` | Custom Viz (`show_custom_visualizations_page`) | Custom Viz | PNG bytes of the last generated plot |
| `pipeline_{file_path_escaped}` | View Data (`_render_transformation_pipeline`) | View Data | List of transformation step dicts for a given file |
| `ttest_result_{state_prefix}` | View Data (`_render_statistical_tests`) | View Data | Result dict of last t-test run for a given file |
| `anova_result_{state_prefix}` | View Data | View Data | Result dict of last ANOVA run |
| `mw_result_{state_prefix}` | View Data | View Data | Result dict of last Mann-Whitney run |
| `chi_result_{state_prefix}` | View Data | View Data | Result dict of last Chi-square run |
| `nav_{path}` | View Data | View Data | Selected value of each folder navigation dropdown |
| `up_nav_{path}` | Upload | Upload | Selected value of each folder navigation dropdown |
| `cv_nav_{path}` | Custom Viz | Custom Viz | Selected value of each folder navigation dropdown |
| `viz_sort_by` | Visualizations | Visualizations | Selected sort order in the gallery |
| `viz_view_mode` | Visualizations | Visualizations | Selected view mode (Gallery/Grid/List) |

**All session state is cleared when the user refreshes the browser page or closes the tab.**

---

## 12. Data Transformation Pipeline

The Transformation Pipeline Builder (in the View Data page) allows users to apply a sequence of operations to the loaded tabular data non-destructively. The original data is never modified on GitHub.

### Available Operations

#### Filter
Reduces rows based on a condition applied to a single column.

| Input | Description |
|---|---|
| Column | The column to filter on |
| Operator | One of: `==`, `!=`, `>`, `>=`, `<`, `<=`, `contains` |
| Value | The comparison value (coerced to numeric if the column is numeric) |

The `contains` operator performs a case-insensitive substring search on the string representation of the column values.

#### Groupby
Aggregates rows by grouping columns.

| Input | Description |
|---|---|
| Group columns | Columns to group by (`groupby()`) |
| Target numeric columns | Columns to aggregate (if empty, a `count` column is produced) |
| Aggregation function | One of: `mean`, `sum`, `median`, `max`, `min` |

#### Normalize
Adds a new column with normalized values (does not replace the original column).

| Input | Description |
|---|---|
| Numeric columns | Columns to normalize |
| Method | `z-score`: `(x - mean) / std` · `min-max`: `(x - min) / (max - min)` |

Output column names: `{original}_zscore` or `{original}_minmax`.

#### Log Transform
Adds a new column with natural-log-transformed values.

| Input | Description |
|---|---|
| Numeric columns | Columns to transform |
| Offset | Constant added before taking the log (default: 1.0). Prevents `log(0)` errors. |

Output column name: `{original}_log`. Raises an error if any shifted value would be ≤ 0.

### Pipeline Behavior
- Steps are **added** with the "Add step" button, **removed** (last step) with "Remove last", or fully reset.
- The pipeline table shows all current steps.
- After adding steps, a "Transformed preview (first 100 rows)" is displayed.
- The transformed DataFrame is passed to the Statistical Test Toolkit.

---

## 13. Statistical Test Toolkit

Located in the View Data page, below the Transformation Pipeline. Operates on the (potentially transformed) DataFrame.

### t-test (Independent Samples)

- **Requirements**: One numeric column (values), one categorical/grouping column, exactly 2 groups selected.
- **Process**:
  1. Levene's test for equal variances → decides between equal-variance and Welch's t-test.
  2. Shapiro-Wilk normality test run per group (if group size ≥ 3).
  3. `scipy.stats.ttest_ind` run with `equal_var` set by Levene p-value > 0.05.
- **Output** (JSON): `test`, `groups`, `assumptions` (Shapiro p-values, Levene p-value), `statistic`, `pvalue`.

### ANOVA (One-Way)

- **Requirements**: One numeric column, one grouping column, 2 or more groups selected.
- **Process**:
  1. Shapiro-Wilk normality per group.
  2. Levene's test for equal variances.
  3. `scipy.stats.f_oneway` on all selected groups.
- **Output** (JSON): `test`, `groups`, `assumptions`, `statistic`, `pvalue`.

### Mann-Whitney U Test

- **Requirements**: One numeric column, one grouping column, exactly 2 groups selected.
- **Process**: `scipy.stats.mannwhitneyu` with `alternative="two-sided"`.
- **Output** (JSON): `test`, `groups`, `assumptions` (independent groups, ordinal/continuous response), `statistic`, `pvalue`.

### Chi-Square Test of Independence

- **Requirements**: Two categorical columns.
- **Process**: `pandas.crosstab` to build contingency table → `scipy.stats.chi2_contingency`.
- **Output** (JSON): `test`, `assumptions` (min expected frequency, whether all expected ≥ 5), `statistic`, `pvalue`, `contingency_table`.

---

## 14. Supported File Types

### Upload Page (files that can be uploaded)

| Extension | Type |
|---|---|
| `.xlsx` | Excel workbook |
| `.csv` | Comma-separated values |
| `.txt` | Plain text |
| `.dat` | Data file (plain text) |
| `.jpg` | JPEG image |
| `.png` | PNG image |

### View Data Page (files that can be previewed)

| Extension | Preview Style | Data operations |
|---|---|---|
| `.xlsx`, `.xls` | Interactive dataframe | Yes (insights, pipeline, stats) |
| `.csv` | Interactive dataframe | Yes (insights, pipeline, stats) |
| `.txt`, `.md`, `.dat` | Read-only text area | No |
| `.docx` | Read-only extracted plain text | No |
| `.jpg`, `.jpeg`, `.png` | Inline image | No |
| Other | Download only | No |

### Custom Visualizations (file selection from repo)

Only `.xlsx` and `.csv` files are shown in the repository file navigator.

---

## 15. Dependencies & Versions

All dependencies are pinned in `requirements.txt`:

```
streamlit==1.24.1
requests==2.31.0
pandas==2.1.1
openpyxl==3.1.2
matplotlib==3.7.3
seaborn==0.12.2
Pillow==9.5.0
numpy==1.26.0
setuptools>=68.0.0
scipy==1.11.3
```

**To upgrade a dependency**, update the version in `requirements.txt`, re-run `pip install -r requirements.txt`, and test thoroughly — Streamlit APIs can contain breaking changes between minor versions.

---

## 16. Known Limitations & Notes for Future Maintainers

### 1. No Overwrite on Upload
The upload page skips files that already exist at the target path. To replace a file, delete it manually from the `Chakrapani2122/Data` GitHub repository first, then re-upload.

### 2. GitHub API Rate Limits
The GitHub REST API enforces rate limits (5,000 requests/hour for authenticated requests). The `@st.cache_data(ttl=300)` decorator mitigates this by caching responses for 5 minutes. If many users access the app simultaneously, rate limits could be hit. Consider increasing the TTL or implementing a shared API token with a higher rate limit.

### 3. Large Files
GitHub's API has a **25 MB limit** for file uploads via the Contents API (used here). For larger files, the GitHub Git Data API (blobs) would be needed. Files over 1 MB may also be slow to load via the `download_url` fallback.

### 4. Session Token Lifetime
The GitHub PAT stored in `st.session_state` is cleared when the user refreshes the browser or the Streamlit session expires. There is no persistent login. Users must re-enter the token each session.

### 5. Data Schedule is Local-Only
`research_team_data.xlsx` lives in the local `App/` directory and is not synced to the data repository. Changes to the schedule require editing this file and redeploying the application.

### 6. Visualization Name Uniqueness
When saving a visualization in the Custom Viz page, the name is used as the PNG filename and as the key in `descriptions.xml`. If the same name is used twice, the second upload will **overwrite** the existing entry in the XML (but it does **not** currently overwrite the PNG — the upload will fail with a non-201 status since the file already exists). Best practice: always use unique, descriptive names.

### 7. `.visualizations` Folder Not Protected
The `visualizations/` folder in the data repository is managed by the app. Manually adding or deleting files there outside of the application may cause inconsistencies between the PNG files and `descriptions.xml`.

### 8. Streamlit Version Compatibility
The code contains one compatibility shim for `st.image(use_column_width=...)` vs `st.image(use_container_width=...)`. The `use_column_width` parameter was deprecated in newer Streamlit versions. The current pinned version (1.24.1) still supports it but future upgrades should use `use_container_width=True` exclusively.

### 9. `research_team_data.xlsx` Must Exist
If this file is missing from the project root, the Data Schedule page will throw an unhandled `FileNotFoundError` exception. Always ensure this file is present before deploying. Consider adding a `try/except` block if the file may not always be present.

### 10. Pair Plot Disabled in Comparative Mode
The `Pair Plot` type is explicitly removed from the available plot types when comparative (side-by-side) mode is enabled. This is intentional — `sns.pairplot` returns a `PairGrid` object, not a standard `Figure`, and cannot be rendered on a subplot `Axes`.

---

## 17. About the Lab

The **Soil Microbial Agroecology Lab (SMAL)** at Kansas State University is dedicated to advancing soil health through comprehensive research on water efficiency, nutrient and energy balance, and climate change.

**Lab Director**: Dr. Charles (Chuck) Rice  
- University Distinguished Professor  
- Vanier University Professorship at Kansas State University  
- Professor of Soil Microbiology, Department of Agronomy  
- Co-winner of the 2007 Nobel Peace Prize (IPCC contribution)  
- Past President, Soil Science Society of America (2011)  
- Published over 100 scholarly publications  
- Fellow: Soil Science Society of America, American Society of Agronomy, AAAS  

**Contact:**  
Address: 2004 Throckmorton PSC, 1712 Claflin Road, Manhattan, KS 66506-0110  
Phone: +1 (785) 532-6101  
Email: agronomy@k-state.edu  
Website: https://www.ksusoilmicrobes.com/

---

*End of Documentation*
