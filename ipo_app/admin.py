from django.contrib import admin
from .models import IPO, SimilarIPO, HistoricalIPO

@admin.register(IPO)
class IPOAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'issue_price', 'open_date', 'status', 'predicted_gain']
    list_filter = ['status', 'sector']
    search_fields = ['company_name']

@admin.register(SimilarIPO)
class SimilarIPOAdmin(admin.ModelAdmin):
    list_display = ['ipo', 'similar_ipo_name', 'similarity_score', 'similar_listing_gains_percentage']

@admin.register(HistoricalIPO)
class HistoricalIPOAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'listing_date', 'listing_gains_percent', 'issue_type']
