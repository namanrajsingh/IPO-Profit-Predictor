from django.core.management.base import BaseCommand
from ipo_app.models import IPO, HistoricalIPO
from decimal import Decimal
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json

class Command(BaseCommand):
    help = 'Fetch real IPO data from Chittorgarh'
    def handle(self, *args, **kwargs):
        # self.stdout.write('Fetching upcoming IPOs...')
        # self.fetch_upcoming_ipos()
        self.stdout.write('\n\n-----------------------------------------\n\n')
        self.stdout.write('Fetching closed IPOs...')
        years = [2024,2025]
        # self.fetch_historical_ipos(years)
        self.fetch_closed_ipo(years)
        self.stdout.write(self.style.SUCCESS('IPO data fetch complete!'))

    from django.db import transaction

    @transaction.atomic
    def fetch_upcoming_ipos(self):
        try:
            yr = datetime.now().year
            url = f"https://webnodejs.chittorgarh.com/cloud/report/data-read/118/1/10/{yr}/{yr+1}-{yr+1}/0/all/0?search=&v=02-39"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            data = json.loads(response.text)
            table = data.get("reportTableData", [])
            today = datetime.now().date()

            # Filter IPOs where listing date is empty and opening date >= today
            upcoming_ipos = [
                ipo for ipo in table
                if not ipo.get('~IPO_Listing_date') and datetime.strptime(ipo['Opening Date'], "%b %d, %Y").date() >= today
            ]
            self.stdout.write(f"Found {len(upcoming_ipos)} upcoming IPOs to process")
            created_count,updated_count = 0,0
            for ipo in upcoming_ipos:
                try:
                    company_name = ipo.get('Company')
                    ipo_data = {
                        'company_id': ipo.get('~id'),
                        'company_logo_url': ipo.get("~compare_image"),
                        'issue_type': ipo.get('Issue Type'),
                        'comapny_url_name': ipo.get('~urlrewrite_folder_name'),
                        'open_date': datetime.strptime(ipo['Opening Date'], "%b %d, %Y").date(),
                        'close_date': datetime.strptime(ipo['Closing Date'], "%b %d, %Y").date(),
                        'status': 'upcoming'
                    }
                    ipo_obj, created = IPO.objects.update_or_create(
                        company_name=company_name,
                        defaults=ipo_data
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f"✓ Created: {company_name}"))
                    else:
                        updated_count += 1
                        self.stdout.write(f"✓ Updated: {company_name}")
                        
                except KeyError as e:
                    self.stdout.write(self.style.ERROR(f"✗ Missing field for {ipo.get('Company', 'Unknown')}: {e}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"✗ Error processing {ipo.get('Company', 'Unknown')}: {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(f"Summary: {created_count} created, {updated_count} updated"))
            
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Network error: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected error: {str(e)}"))
            import traceback
            traceback.print_exc()

    def fetch_historical_ipos(self,years):
        created_count,updated_count = 0,0
        try:
            y = years if len(years) < 1 else list(range(years[0], years[1] + 1))
            for year in y :
                url = f"https://webnodejs.chittorgarh.com/cloud/report/data-read/98/1/10/{year}/{year}-{year+1}/0/all/0?search=&v=12-09"
                data =  json.loads(requests.get(url,{'User-Agent': 'Mozilla/5.0'}).text)
                table = data["reportTableData"]
                for ipo in table:
                        try:
                            ipo_data = {
                            'company_id': ipo.get('~id'),
                            'company_name': ipo['Company'],
                            'issue_type': ipo.get('Issue Type', ''),
                            'comapny_url_name': ipo.get('~URLRewrite_Folder_Name'),
                            'open_date': datetime.strptime(ipo['Opening Date'], "%b %d, %Y").date(),
                            'listing_date': datetime.strptime(ipo['Listing Date'], "%b %d, %Y").date(),
                            'issue_size': Decimal(ipo['Issue Amount<br/> (Rs.cr.)']),
                            'issue_price': Decimal(ipo['Issue Price (Rs.)']),
                            'listing_price': Decimal(ipo['Open Price on Listing (Rs.)']),
                            'qib_subscription': Decimal(ipo.get('QIB', 0) or 0 ),
                            'nii_subscription': Decimal(ipo.get('NII', 0) or 0),
                            'retail_subscription': Decimal(ipo.get('RII', 0) or 0),
                            'total_subscription': Decimal(ipo.get('TOTAL', 0) or 0),
                            }

                            ipo_data['listing_gains_rs'] = ipo_data['listing_price'] - ipo_data['issue_price']
                            ipo_data['listing_gains_percent'] = round(ipo_data['listing_gains_rs'] / ipo_data['issue_price'] * 100, 2)

                            hist, created = HistoricalIPO.objects.update_or_create(
                            company_name=ipo_data['company_name'], defaults=ipo_data)
                            if created:
                                created_count += 1
                            else:
                                updated_count += 1
                        
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"✗ Error processing {ipo.get('company_name', ipo['Company'])} of year {year}: {str(e)}"))
                            break
                self.stdout.write(self.style.SUCCESS(f"✓ Created: Year {year}"))
            self.stdout.write(self.style.SUCCESS(f"\nSummary: {created_count} created, {updated_count} updated in year range {years}"))
            resp = {"Success":True}

        except Exception as e:
            resp = {"Success":False, "Error":e}
            self.stdout.write(self.style.ERROR(f"✗ Failed to get Historical data: {e}"))
        
        return resp
    
    def fetch_closed_ipo(self, years=None):
        created_count, updated_count = 0, 0
        try:
            if years and len(years) > 1:
                start_year, end_year = years[0], years[1]
                historical_ipos = HistoricalIPO.objects.filter(
                    listing_date__year__gte=start_year,
                    listing_date__year__lte=end_year
                )
            else:
                historical_ipos = HistoricalIPO.objects.all()

            for hist_ipo in historical_ipos:
                url = f"https://www.chittorgarh.com/ipo/{hist_ipo.comapny_url_name}/{hist_ipo.company_id}/"
                
                ipo_data = {
                    'company_id': hist_ipo.company_id,
                    'company_name': hist_ipo.company_name,
                    'company_logo_url': hist_ipo.company_logo_url,
                    'comapny_url_name':hist_ipo.comapny_url_name,
                    'issue_type': hist_ipo.issue_type,
                    'open_date': hist_ipo.open_date,
                    'listing_date': hist_ipo.listing_date,
                    'issue_price': hist_ipo.issue_price,
                    'issue_size': hist_ipo.issue_size,
                    'listing_price': hist_ipo.listing_price,
                    'qib_subscription': hist_ipo.qib_subscription,
                    'nii_subscription': hist_ipo.nii_subscription,
                    'retail_subscription': hist_ipo.retail_subscription,
                    'total_subscription': hist_ipo.total_subscription,
                    'listing_gains_rs':hist_ipo.listing_gains_rs,
                    'listing_gains_percent':hist_ipo.listing_gains_percent,
                    'profit': None,  # Set default or fill from other sources if available
                    'pe_ratio': None,  # Set default or fill from other sources if available
                    'status': 'closed',
                }

                # ipo_obj, created = IPO.objects.update_or_create(
                #     company_name=hist_ipo.company_name,
                #     defaults=ipo_data
                # )
                created = True
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(self.style.SUCCESS(f"Summary: {created_count} created, {updated_count} updated from HistoricalIPO."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Failed to fetch and add closed IPOs: {str(e)}"))

        return {'created': created_count, 'updated': updated_count}
