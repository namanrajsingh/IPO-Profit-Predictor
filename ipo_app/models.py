from django.db import models
from django.utils import timezone


class IPO(models.Model):
    company_id = models.CharField(max_length=50, blank=True)#
    company_logo_url = models.CharField(max_length=200, blank=True)#
    company_name = models.CharField(max_length=200)#
    issue_type = models.CharField(max_length=50, blank=True)#
    comapny_url_name = models.CharField(max_length=200, blank=True)#
    open_date = models.DateField(null=True, blank=True)#
    close_date = models.DateField(null=True, blank=True)#
    listing_date = models.DateField(null=True, blank=True)#
    
    issue_price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)#
    issue_size = models.DecimalField(max_digits=10, decimal_places=2, help_text="In crores",null=True, blank=True)
    listing_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lot_size = models.IntegerField(null=True, blank=True)
    
    qib_subscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)#
    nii_subscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)#
    retail_subscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)#
    total_subscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)#
    
    listing_gains_rs = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)#
    listing_gains_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="In percentage")#
    sector = models.CharField(max_length=100,null=True, blank=True)
    lead_manager = models.CharField(max_length=200, blank=True)
    registrar = models.CharField(max_length=200, blank=True)
    
    revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="In crores")
    profit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="In crores")
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    predicted_gain = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prediction_confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('listed', 'Listed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['open_date']
        # verbose_name = "IPO"
        # verbose_name_plural = "IPOs"
    
    def __str__(self):
        return self.company_name
    

class SimilarIPO(models.Model):
    ipo = models.ForeignKey(IPO, on_delete=models.CASCADE, related_name='similar_ipos')
    similar_ipo_name = models.CharField(max_length=200)
    similarity_score = models.DecimalField(max_digits=5, decimal_places=2)
    similar_qib = models.DecimalField(max_digits=10, decimal_places=2)
    similar_hni = models.DecimalField(max_digits=10, decimal_places=2)
    similar_retail = models.DecimalField(max_digits=10, decimal_places=2)
    similar_issue_size = models.DecimalField(max_digits=10, decimal_places=2)
    similar_gmp = models.DecimalField(max_digits=10, decimal_places=2)
    similar_listing_gains_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    similar_sector = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.similar_ipo_name} ({self.similarity_score}%)"

class HistoricalIPO(models.Model):
    company_id = models.CharField(max_length=50, blank=True)
    company_name = models.CharField(max_length=200)
    company_logo_url = models.CharField(max_length=200, blank=True)
    issue_type = models.CharField(max_length=50, blank=True)
    comapny_url_name = models.CharField(max_length=200, blank=True)
    
    open_date = models.DateField(null=True, blank=True)
    listing_date = models.DateField(null=True, blank=True)
    
    issue_size = models.DecimalField(max_digits=10, decimal_places=2)
    issue_price = models.DecimalField(max_digits=10, decimal_places=2)
    listing_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    qib_subscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nii_subscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    retail_subscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_subscription = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    listing_gains_rs = models.DecimalField(max_digits=10, decimal_places=2)
    listing_gains_percent = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-listing_date']
    
    def __str__(self):
        return f"{self.company_name} - {self.listing_gains_percent}%"