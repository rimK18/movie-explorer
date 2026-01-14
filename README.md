# Movie Explorer — Cloud Data Web Application

## Overview

**Movie Explorer** is a cloud-based web application that allows users to explore a movie catalog using SQL queries on Google BigQuery, combined with an interactive Streamlit interface.

The project was developed in an academic context to demonstrate end-to-end cloud application design, from data querying to deployment.

---

## What this project demonstrates

This project focuses on **architecture and engineering skills** rather than data ownership.

It demonstrates the ability to:

* Query analytical datasets using **BigQuery SQL** (joins, aggregations, filters)
* Build interactive data applications with **Streamlit**
* Integrate an external **REST API** (The Movie Database)
* Containerize an application with **Docker**
* Deploy a serverless service on **Google Cloud Run**
* Manage configuration and secrets using environment variables

---

## Key Features

**Movie search with SQL-based filtering:**
* Title (text search)
* Language
* Genre
* Release year
* Minimum average rating (JOIN + aggregation)

**Movie detail view:**
* Synopsis
* Poster
* Metadata retrieved from **The Movie Database (TMDB) API**

**Dockerized application**

**Cloud deployment on Google Cloud Run**

---

## High-Level Architecture

```
User
↓
Streamlit UI
↓
BigQuery (movies and ratings)
↓
TMDB API (movie details)
```

**Deployment:**
* Docker container
* Google Cloud Run (serverless)

---

## Dataset and Availability

This application was originally built using a Google BigQuery dataset (movies and ratings) provided during an academic course.

⚠️ **The original BigQuery tables are not included in this repository and may no longer be publicly available.**

The purpose of this repository is to showcase:
* Query logic
* Cloud architecture
* Application structure
* Deployment strategy

Running the application locally or in the cloud **requires access to a compatible BigQuery dataset** with the expected schema.

---

## Local Setup (Optional)

**Prerequisites:**
* Python 3.9 or higher
* Docker
* Google Cloud SDK
* Access to a Google Cloud project with BigQuery enabled

**Environment Variables:**

```bash
TMDB_API_KEY=your_tmdb_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json
GCP_PROJECT_ID=movie-project-453208
BQ_MOVIES_TABLE=movie-project-453208.movies_dataset.movies
BQ_RATINGS_TABLE=movie-project-453208.ratings_dataset.ratings
```

**Run Locally:**

```bash
pip install -r requirements.txt
python -m streamlit run app/main.py
```

If BigQuery is not available, the application displays a clear message instead of failing silently.

---

## Run with Docker

```bash docker build -t movie-explorer . docker run -p 8080:8080 movie-explorer ```

Access the application at: **http://localhost:8080\*\*

---

## Cloud Deployment (Google Cloud Run)

```bash
docker tag movie-explorer gcr.io/<PROJECT_ID>/movie-explorer
docker push gcr.io/<PROJECT_ID>/movie-explorer

gcloud run deploy movie-explorer
--image gcr.io/<PROJECT_ID>/movie-explorer
--platform managed
--region europe-west6
--allow-unauthenticated ```

---

## Technology Stack

* **Python 3.9**
* **Google BigQuery**
* **Streamlit**
* **Docker**
* **Google Cloud Run**
* **The Movie Database (TMDB) API**

---

## Context

Academic project developed as part of the course **Cloud and Advanced Analytics — 2025**

**Author:** Karim Bellamri

