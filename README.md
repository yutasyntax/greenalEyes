## GreenalEyes

GreenalEyes is a web app that lets you analyze vegetation coverage anywhere in the world. Just select a location on the map—the app fetches satellite imagery and uses computer vision to calculate how much of the area is covered in green vegetation.
This tool was developed as part of a personal project focused on urban greening.

## Features
- Select any location interactively on the map
- Retrieve satellite imagery of the selected area
- Analyze vegetation coverage using OpenCV-based green pixel detection
- Display green coverage percentage
- Visualize results with a heatmap overlay

## File Structure
- `main.py`: Main application file containing the Streamlit logic and UI components
- `requirements.txt`: Lists required Python packages
- `.streamlit/`: Configuration directory for Streamlit
- `.gitignore`: Excludes unnecessary or sensitive files (e.g. `.idea/`)
- `README.md`: Project overview and usage instructions

## How to Run

1. Clone the repository:  
   `git clone https://github.com/yutasyntax/greenalEyes.git`  
   `cd greenalEyes`

2. (Optional) Create and activate a virtual environment:  
   `python -m venv venv`  
   `source venv/bin/activate`  *(On Windows: `venv\Scripts\activate`)*

3. Install dependencies:  
   `pip install -r requirements.txt`

4. Run the Streamlit app:  
   `streamlit run main.py`

## Tech Stack

- Python
- Streamlit
- OpenCV
- Folium
- Satellite Imagery APIs

## Example Use Cases

- Estimating the green coverage of urban neighborhoods
- Visualizing before/after effects of city greening projects
- Supporting environmental research with quick vegetation analytics

## Author

Created by [Yuta Asai](https://www.linkedin.com/in/yutasyntax/)
