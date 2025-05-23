# Formula 1 Visualization Website

This project is a Formula 1 Data Visualization Website built with **Django** and powered by the **FastF1 API**. The site provides interactive and insightful visualizations of Formula 1 racing data, offering fans, analysts, and developers a way to explore detailed statistics and race analytics from recent F1 seasons.

## Features

- Select different types of graphs including:
  - Lap time distributions  
  - Speed comparisons  
  - Qualifying results  
  - Position changes throughout the race  
- Filter data by driver, Grand Prix, and season  
- Visualize performance in an intuitive format  

## Tech Stack

- **Backend:** Django (Python)  
- **Data Source:** FastF1 API  
- **Visualization:** Matplotlib, Plotly  
- **Frontend:** HTML, CSS, Bootstrap  

## Setup Instructions

### Prerequisites

- Python 3.9+  
- pip  
- Virtualenv (recommended)  

### Installation

```bash
# Clone the repository
git clone https://github.com/KianFatemi/Formula1-Data-Website.git
cd Formula1-Data-Website

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  

# Install dependencies
pip install -r requirements.txt

# Run Django migrations
python manage.py migrate

# Start development server
python manage.py runserver
```
## Usage
Open http://127.0.0.1:8000/speedtrace in your browser

Choose a season, Grand Prix, and driver(s)

Select the graph type you want to view

Analyze lap-by-lap data and driver performance
