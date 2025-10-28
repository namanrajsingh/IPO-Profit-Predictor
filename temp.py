
import requests,json
from bs4 import BeautifulSoup


class hist_ipo:
    comapny_url_name= 'midwest-ipo'
    company_id = '2150'
url = f"https://www.chittorgarh.com/ipo/{hist_ipo.comapny_url_name}/{hist_ipo.company_id}/"
html_content =  requests.get(url,{'User-Agent': 'Mozilla/5.0'}).text
soup = BeautifulSoup(html_content, 'html.parser')



# Extract revenue and profit from financialTable
financial_table = soup.find('table', {'id': 'financialTable'})
revenue, profit = None, None
if financial_table:
    rows = financial_table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 1:
            label = cells[0].get_text(strip=True).lower()
            # Example: Look for 'total income' as revenue
            if 'total income' in label or 'revenue' in label:
                # typically multiple columns, take latest or required column (e.g. 2nd or 3rd)
                revenue = cells[1].get_text(strip=True)  # adapt index for right column
            elif 'profit after tax' in label or 'pat' in label:
                profit = cells[1].get_text(strip=True)

# Extract PE ratio from KPI or analysis table
kpi_table = soup.find('table', {'id': 'analysisTable'}) or soup.find('table', {'id': 'peRatioTable'})
pe_ratio = None
if kpi_table:
    rows = kpi_table.find_all('tr')
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) > 1:
            if 'pe ratio' in cells[0].get_text(strip=True).lower():
                pe_ratio = cells[1].get_text(strip=True)
                break

print(f"Revenue: {revenue}")
print(f"Profit: {profit}")
print(f"PE Ratio: {pe_ratio}")