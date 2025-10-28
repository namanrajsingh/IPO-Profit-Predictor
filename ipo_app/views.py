from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
from .models import IPO, SimilarIPO, HistoricalIPO
from .serializers import IPOSerializer, HistoricalIPOSerializer
from django.db.models.functions import ExtractYear

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ipo_model.pkl')
try:
    with open(MODEL_PATH, 'rb') as f:
        ml_model = pickle.load(f)
except:
    ml_model = None

class IPOViewSet(viewsets.ModelViewSet):
    queryset = IPO.objects.all()
    serializer_class = IPOSerializer

    def get_queryset(self):
        queryset = IPO.objects.all()
        upcoming = self.request.query_params.get('upcoming', None)
        if upcoming:
            queryset = queryset.filter(open_date__gte=datetime.now().date())
        return queryset

    def perform_create(self, serializer):
        ipo = serializer.save()
        if ipo.qib_subscription:
            prediction = predict_listing_gain(ipo)
            ipo.predicted_gain = prediction['predicted_gain']
            ipo.prediction_confidence = prediction['confidence']
            ipo.save()

class HistoricalIPOViewSet(viewsets.ModelViewSet):
    queryset = HistoricalIPO.objects.all()
    serializer_class = HistoricalIPOSerializer

@api_view(['POST'])
def predict_api(request):
    data = request.data
    features = np.array([[
        float(data.get('qib_subscription', 0)),
        float(data.get('hni_subscription', 0)),
        float(data.get('retail_subscription', 0)),
        float(data.get('issue_size', 0)),
        float(data.get('issue_price', 0)),
        float(data.get('gmp', 0)),
        float(data.get('market_sentiment', 19500))
    ]])

    if ml_model:
        predicted_gain = ml_model.predict(features)[0]
        confidence = 70.0
    else:
        predicted_gain = (features[0][0]*0.3 + features[0][1]*0.2 + features[0][2]*0.1 + features[0][5]*0.4)*2.5
        confidence = 60.0

    return Response({
        'predicted_gain': round(predicted_gain, 2),
        'confidence': confidence,
        'message': 'Prediction successful'
    })

def predict_listing_gain(ipo):
    try:
        features = np.array([[
            float(ipo.qib_subscription),
            float(ipo.hni_subscription),
            float(ipo.retail_subscription),
            float(ipo.issue_size),
            float(ipo.issue_price),
            float(ipo.gmp),
            19500
        ]])
        if ml_model:
            gain = ml_model.predict(features)[0]
            return {'predicted_gain': gain, 'confidence': 70}
        else:
            gain = (ipo.qib_subscription*0.3 + ipo.hni_subscription*0.2 + ipo.retail_subscription*0.1 + ipo.gmp*0.4)*2.5
            return {'predicted_gain': round(gain, 2), 'confidence': 60}
    except:
        return {'predicted_gain': 0, 'confidence': 0}

def home(request):
    # upcoming_ipos = IPO.objects.filter(status='upcoming')
    return render(request, 'home.html')

from datetime import date   # <--- using 'date', not 'datetime'

def ipo_upcomming(request):
    upcoming_ipos = IPO.objects.filter(status='upcoming')
    today = date.today()
    ipo_list = []
    for ipo in upcoming_ipos:
        if ipo.open_date:
            days_remaining = (ipo.open_date - today).days
        else:
            days_remaining = None
        ipo_list.append({
            'object': ipo,
            'days_remaining': days_remaining,
        })
    return render(request, 'ipo_upcomming.html', {'upcoming_ipos': ipo_list})


def ipo_past(request):
    past_ipos = HistoricalIPO.objects.filter()
    years = (
        HistoricalIPO.objects
        .exclude(listing_date__isnull=True)
        .annotate(year=ExtractYear('listing_date'))
        .values_list('year', flat=True)
        .distinct()
        .order_by('-year')
    )
    return render(request, 'ipo_past.html', {'past_ipos': past_ipos,"years":years})

def ipo_detail(request, company_id):
    ipo = IPO.objects.get(company_id=company_id)
    similar_ipos = ipo.similar_ipos.all()
    return render(request, 'ipo_detail.html', {'ipo': ipo, 'similar_ipos': similar_ipos})
