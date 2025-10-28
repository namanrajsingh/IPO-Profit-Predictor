import requests
from bs4 import BeautifulSoup
from decimal import Decimal

# Sector keywords mapping
SECTOR_KEYWORDS = {
    'Mining': ['mining', 'granite', 'stone', 'ores', 'natural resources', 'minerals', 'quarry', 'excavation'],
    'Technology': ['software', 'it', 'technology', 'digital', 'it services', 'tech', 'saas', 'cloud computing'],
    'Pharmaceuticals': ['pharmaceutical', 'biotech', 'laboratory', 'clinical', 'drug', 'medicine', 'healthcare'],
    'Finance': ['bank', 'finance', 'nbfc', 'financial services', 'investment', 'lending', 'credit'],
    'Infrastructure': ['construction', 'infrastructure', 'real estate', 'builder', 'housing', 'property'],
    'Energy': ['energy', 'power', 'electricity', 'solar', 'renewable', 'oil', 'gas', 'coal'],
    'Consumer Goods': ['fmcg', 'consumer goods', 'consumer products', 'retail', 'e-commerce'],
    'Automobiles': ['automobile', 'auto', 'vehicle', 'car', 'bike', 'automotive'],
    'Chemical': ['chemical', 'fertilizer', 'agrochemical', 'pesticide'],
    'Telecom': ['telecom', 'telecommunication', 'mobile', 'network'],
    'Media': ['media', 'entertainment', 'broadcasting', 'film', 'content'],
    'Manufacturing': ['manufacturing', 'production', 'factory', 'industrial'],
    'Textiles': ['textile', 'apparel', 'garment', 'fabric', 'clothing'],
    'Education': ['education', 'training', 'learning', 'institute', 'school', 'college'],
    'Logistics': ['logistics', 'transportation', 'shipping', 'supply chain', 'courier'],
}

class hist_ipo:
    comapny_url_name = 'wework-india-management-ipo'
    company_id = '2014'

def clean_number(text):
    """Remove commas and convert to Decimal"""
    if not text:
        return None
    try:
        # Remove commas and spaces, convert to Decimal
        cleaned = text.strip().replace(',', '')
        return Decimal(cleaned)
    except:
        return None

def classify_sector(text):
    """Classify sector based on keyword matching"""
    if not text:
        return 'Unknown'
    
    normalized_text = text.lower()
    sector_scores = {}
    
    for sector, keywords in SECTOR_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in normalized_text:
                score += 1
        if score > 0:
            sector_scores[sector] = score
    
    if sector_scores:
        return max(sector_scores, key=sector_scores.get)
    
    return 'Unknown'

def extract_ipo_data(company_url_name, company_id):
    """
    Extract all financial data, KPIs, and sector from IPO page
    """
    url = f"https://www.chittorgarh.com/ipo/{company_url_name}/{company_id}/"
    html_content = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(html_content, 'html.parser')
    
    result = {
        'financial_data': {},
        'kpis': {},
        'sector': 'Unknown'
    }
    
    # 1. Extract Financial Data (Assets, Profit, Total Income for all years)
    financial_table = soup.find('table', {'id': 'financialTable'})
    if financial_table:
        rows = financial_table.find_all('tr')
        
        # Get column headers (dates/periods)
        header_row = rows[0]
        periods = [td.get_text(strip=True) for td in header_row.find_all('td')[1:]]  # Skip first column (label)
        
        # Initialize data structure
        for period in periods:
            result['financial_data'][period] = {}
        
        # Extract data rows
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) > 1:
                label = cells[0].get_text(strip=True)
                
                # Extract values for each period
                for i, period in enumerate(periods):
                    if i + 1 < len(cells):
                        value = clean_number(cells[i + 1].get_text(strip=True))
                        result['financial_data'][period][label] = value
    
    # 2. Extract Key Performance Indicators (KPIs)
    kpi_tables = soup.find_all('table', class_='table table-bordered table-striped table-hover w-auto')
    
    for table in kpi_tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                value_text = cells[1].get_text(strip=True)
                
                # Try to convert to number, otherwise keep as string
                value = clean_number(value_text)
                if value is None:
                    value = value_text
                
                result['kpis'][label] = value
    
    # 3. Extract Sector from "About Company" section
    about_section = soup.find('div', id='about-company-section')
    if about_section:
        paragraphs = about_section.find_all('p')
        company_text = ' '.join(p.get_text(strip=True) for p in paragraphs)
        result['sector'] = classify_sector(company_text)
    
    return result

# Run extraction
data = extract_ipo_data(hist_ipo.comapny_url_name, hist_ipo.company_id)

# Print results
print("=" * 80)
print("FINANCIAL DATA (ALL YEARS)")
print("=" * 80)
for period, values in data['financial_data'].items():
    print(f"\n{period}:")
    for label, value in values.items():
        print(f"  {label}: {value}")

print("\n" + "=" * 80)
print("KEY PERFORMANCE INDICATORS")
print("=" * 80)
for label, value in data['kpis'].items():
    print(f"{label}: {value}")

print("\n" + "=" * 80)
print(f"SECTOR: {data['sector']}")
print("=" * 80)

# Access specific data examples:
print("\n" + "=" * 80)
print("SPECIFIC DATA EXAMPLES:")
print("=" * 80)

# Get latest period's profit
if data['financial_data']:
    latest_period = list(data['financial_data'].keys())[0]
    print(f"\nLatest Period: {latest_period}")
    print(f"Profit After Tax: {data['financial_data'][latest_period].get('Profit After Tax', 'N/A')}")
    print(f"Assets: {data['financial_data'][latest_period].get('Assets', 'N/A')}")
    print(f"Total Income: {data['financial_data'][latest_period].get('Total Income', 'N/A')}")

# Get PE Ratio
print(f"\nPE Ratio: {data['kpis'].get('PE x', 'N/A')}")
print(f"ROE: {data['kpis'].get('ROE', 'N/A')}")
print(f"ROCE: {data['kpis'].get('ROCE', 'N/A')}")
