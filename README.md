# Autonomous Claims Processing Agent

## Overview

This project is a lightweight AI-powered claims processing agent built
with **Streamlit** and **Groq Llama 3.3**. It extracts information from
FNOL (First Notice of Loss) documents, validates mandatory fields,
applies business rules, and recommends the appropriate processing route.

## Features

-   Extracts structured data from PDF/TXT FNOL documents.
-   Identifies missing mandatory fields.
-   Applies routing rules:
    -   **Fast-track**: Estimated damage \< ₹25,000.
    -   **Manual Review**: Missing mandatory fields.
    -   **Investigation Flag**: Description contains keywords such as
        *fraud*, *inconsistent*, or *staged*.
    -   **Specialist Queue**: Claim type is *Injury*.
    -   **Standard Review**: All other valid claims.
-   Displays extracted JSON.
-   Download processed result as JSON.

## Tech Stack

-   Python 3.10+
-   Streamlit
-   Groq API
-   Llama 3.3 70B Versatile
-   PyPDF

## Project Approach

1.  Upload an FNOL PDF or TXT document.
2.  Extract raw text from the document.
3.  Send the text to the Groq Llama model to extract structured JSON.
4.  Validate mandatory fields.
5.  Execute business rules.
6.  Display the routing decision and allow JSON download.

## Steps to Run

### 1. Clone the repository

``` bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create a virtual environment

``` bash
python -m venv .venv
```

Windows:

``` bash
.venv\Scripts\activate
```

Linux/macOS:

``` bash
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure Groq API Key

Create a `.env` file:

    GROQ_API_KEY=your_groq_api_key

### 5. Run the application

``` bash
streamlit run data_extracter_updated.py
```

### 6. Use the application

-   Upload an FNOL PDF or TXT file.
-   Click **Run Autonomous Agent**.
-   Review the extracted fields, routing decision, and download the JSON
    output.
