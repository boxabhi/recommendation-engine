from django.shortcuts import render
import pandas as pd
from .models import UserActivity, Product
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import get_cached_recommendations
from .collaborative import *
from .content_based import *
from .serializer import *


def index(request):
    return render(request, 'index.html')

class LogUserActivity(APIView):
    def get(self, request):
        
        if request.GET.get('product_id') is None:
            return Response({"message": "id required!"}, status=201)

       

        data = {
            "user"  : request.user.id,
            "product" : request.GET.get('product_id'),
            "action" : "click"
        }
        serializer = UserActivitySerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Automatically set the logged-in user
            activities = UserActivity.objects.filter(user = request.user)
            if activities.count() > 5:
                activities.last().delete()
            return Response({"message": "User activity logged successfully!"}, status=201)
        return Response(serializer.errors, status=200)
    



def get_similar_products_by_user_activity(user_id, top_n=10):
    try:
        user_activities = UserActivity.objects.filter(user_id=user_id)
        if not user_activities.exists():
            return []
        product_ids = user_activities.values_list('product', flat=True).distinct()
        user_products = Product.objects.filter(id__in=product_ids)
        descriptions = [product.description for product in user_products]
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(descriptions)
        

        all_products = list(Product.objects.all())
        all_product_descriptions = [product.description for product in all_products]
        
        all_tfidf_matrix = tfidf_vectorizer.transform(all_product_descriptions)
        
        similar_products = set()
        
        for i, user_product in enumerate(user_products):
            cosine_sim = cosine_similarity(tfidf_matrix[i], all_tfidf_matrix).flatten()
            similar_indices = cosine_sim.argsort()[-top_n-1:-1][::-1]
            for idx in similar_indices:
                # Directly compare the products in all_products using their IDs
                similar_product = all_products[idx]
                if similar_product != user_product:  # Ensure the product itself is not recommended
                    similar_products.add(similar_product)
        
        # Convert the set of similar products to a list
        similar_products = list(similar_products)
        
        # Step 4: Return the most similar products
        return similar_products
    
    
    except Exception as e:
        import sys
        import os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        return []  # Return empty list in case of error
    


class ProductAPI(APIView):
    def get(self, request):
        user_id = 1
        all_products = ProductSerializer(Product.objects.all().order_by('?')[:10], many = True)
        products = get_similar_products_by_user_activity(user_id)
        #products.reverse()
        serializer = ProductSerializer(products, many=True)
        return Response({"all_products" : all_products.data , "similar_products":serializer.data})