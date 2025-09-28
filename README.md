# 🎯 Internship Recommendation Engine

A smart internship recommendation system that scrapes the latest internship opportunities and provides personalized recommendations based on your skills and preferences.

## ✨ Features

- **🔍 Smart Scraping**: Automatically finds the latest internships from multiple job boards
- **🎯 Personalized Matching**: Matches internships based on your skills and preferences  
- **📊 Smart Ranking**: Ranks opportunities by relevance, stipend, and recency
- **💰 Stipend Analysis**: Extracts and analyzes stipend information
- **📍 Location Filtering**: Supports location-based filtering including remote options
- **📈 Interactive Dashboard**: Beautiful Streamlit interface with charts and statistics
- **📥 Export Options**: Download results as CSV for further analysis

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Scraping**: jobspy library
- **Data Processing**: pandas, numpy
- **Visualization**: plotly
- **ML/Analytics**: scikit-learn

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager

## 🚀 Installation

### Quick Installation
Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

### Manual Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip3 install streamlit pandas numpy scikit-learn requests beautifulsoup4 lxml python-dateutil plotly
   ```

3. **Try to install jobspy (optional)**:
   ```bash
   pip3 install jobspy
   ```
   *Note: If jobspy fails to install, the app will automatically use an alternative scraper*

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Open your browser** and navigate to `http://localhost:8501`

### Test Installation
```bash
python3 test_app.py
```

## 📖 Usage

### 1. Input Your Profile
- Enter your name
- List your skills (comma-separated)
- Specify preferred location
- Select experience level
- Set minimum stipend requirement

### 2. Configure Search Parameters
- Choose number of results to display
- Set maximum age for job postings
- Click "Find My Internships"

### 3. Review Results
- View personalized recommendations
- Analyze stipend and location distributions
- Check relevance scores
- Click "Apply Now" to visit job postings

### 4. Export Data
- Download results as CSV for offline analysis

## 🏗️ Project Structure

```
internship-recommendation-engine/
├── app.py              # Streamlit user interface
├── scraper.py          # Web scraping logic using jobspy
├── filter.py           # Filtering and ranking algorithms
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🔧 How It Works

### 1. Scraping (`scraper.py`)
- Uses jobspy library to scrape from multiple job boards
- Combines user skills with internship keywords for targeted searches
- Filters results to focus on internship positions
- Extracts stipend information from job descriptions
- Calculates relevance scores based on skill matching

### 2. Filtering (`filter.py`)
- Applies user-defined filters (stipend, location, age)
- Calculates ranking scores using weighted criteria:
  - 40% Relevance to user skills
  - 30% Stipend amount
  - 20% Recency of posting
  - 10% Company reputation
- Removes duplicates and low-quality listings

### 3. User Interface (`app.py`)
- Clean, intuitive Streamlit interface
- Real-time search and filtering
- Interactive charts and statistics
- Export functionality

## ⚙️ Configuration

### Customizing Search Sources
Edit `scraper.py` to modify the job boards:
```python
self.sites = ['linkedin', 'indeed', 'zip_recruiter', 'glassdoor']
```

### Adjusting Ranking Weights
Modify `filter.py` to change ranking criteria:
```python
self.weights = {
    'relevance_score': 0.4,    # 40% weight on relevance
    'stipend': 0.3,            # 30% weight on stipend
    'recency': 0.2,            # 20% weight on recency
    'company_reputation': 0.1   # 10% weight on company reputation
}
```

## 🐛 Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'jobspy'**:
   - This is normal! The app automatically falls back to an alternative scraper
   - You'll see a warning message but the app will work fine
   - The alternative scraper provides sample data for demonstration

2. **No internships found**:
   - Try broader skill terms
   - Adjust location preferences
   - Increase maximum age of postings
   - The alternative scraper provides sample data if real scraping fails

3. **Rate limiting errors**:
   - The scraper includes delays to avoid rate limiting
   - If issues persist, try reducing the number of search terms
   - The alternative scraper provides sample data as fallback

4. **Missing stipend information**:
   - Many internships don't specify stipends
   - The system will show "Not specified" for these cases
   - Sample data includes realistic stipend ranges

5. **Streamlit not found**:
   ```bash
   pip3 install streamlit
   ```

6. **Permission denied on install.sh**:
   ```bash
   chmod +x install.sh
   ```

### Performance Tips

- Use specific, relevant skills for better matching
- Limit the number of results if experiencing slow performance
- The system automatically removes duplicates

## 📊 Sample Output

The system provides:
- **Personalized recommendations** ranked by relevance
- **Stipend distribution charts** showing salary ranges
- **Location analysis** with geographic distribution
- **Relevance scores** (0-10) for each opportunity
- **Direct apply links** to job postings

## 🤝 Contributing

Feel free to contribute by:
- Adding new job board sources
- Improving the ranking algorithm
- Enhancing the user interface
- Adding new filtering options

## 📝 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

- This tool is for educational and personal use
- Always verify job postings on official company websites
- Respect the terms of service of job board websites
- The accuracy of scraped data depends on the source websites

## 🆘 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the error messages in the console
3. Ensure all dependencies are properly installed
4. Try with different search parameters

---

**Happy job hunting! 🎉**
