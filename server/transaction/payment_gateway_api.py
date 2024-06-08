import email
from lib2to3.pgen2 import token
from math import prod
from wsgiref import headers
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.http.response import HttpResponseNotFound, JsonResponse
import json
from .models import PlanFeatures, Subscription, Plans, SubscriptionPayment, PlansFeatureUser
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import permissions
from knox.auth import TokenAuthentication
from drf_yasg.utils import swagger_auto_schema
from .subcription_serializer import GetSubscriptionViewSerializer, PlanViewSerializer, PlanFeaturesSerializer
from rest_framework.decorators import action
from datetime import datetime, timedelta, timezone, tzinfo
from rest_framework.response import Response
from django.http import HttpResponse,HttpResponseRedirect
from user.models import User


class PaymentGatway(GenericAPIView):
    serializer_class = GetSubscriptionViewSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    @swagger_auto_schema(tags=['Subscribe Plans'])
    @csrf_exempt
    @action(detail=False, methods=['post'])
    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # import pdb;pdb.set_trace()
            useremail = str(request.user)
            print(useremail)
            check_data = request.data
            YOUR_DOMAIN = 'http://'+request.get_host()+'/'
            SUCCESS_REDIRECT_URL = check_data['success_url']
            FAILURE_REDIRECT_URL = check_data['fail_url']
            pricecome = Plans.objects.get(id=check_data['plans'])
            price_id = pricecome.price_id
            payment1 = stripe.checkout.Session.create(
                    success_url= YOUR_DOMAIN +'api/plan/payment_success?session_id={CHECKOUT_SESSION_ID}&redirect_url='+SUCCESS_REDIRECT_URL+'&useremail='+useremail,
                    cancel_url= YOUR_DOMAIN + 'api/plan/payment_fail?session_id={CHECKOUT_SESSION_ID}&redirect_url='+FAILURE_REDIRECT_URL,
                    line_items=[
                            {
                            "price": price_id,
                            "quantity": 1,
                            },
                        ],
                        mode="subscription",
                        )
            checkout=payment1.url
            checkout_id=payment1.id
            print(checkout_id)
        except Exception as e:
            return JsonResponse({'result': 'fail', 'response': 'Something went wrong, Please check.'}, safe=False)
    
        plans_id = pricecome
        user_id = request.user
        user_email = request.user
        checkout_id=payment1.id
        price_id = price_id
        # import pdb;pdb.set_trace()
        details={'user':user_id,'user_email':user_email, 'plans':plans_id ,'price_id':price_id,'session_id':checkout_id}

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # check=Subscription.objects.filter(plans=request.data['plans'],user=details['user']).count()
            # if check != 0:
            #     return JsonResponse({'result': 'false', 'response': 'You have already get this Subscription'}, safe=False)
            subscription = Subscription.objects.create(user=user_id,user_email=user_email, plans=plans_id ,price_id=price_id,session_id=checkout_id)

            return Response({
                "Checkout Link": checkout,
                "Session Id": checkout_id,
            })

        else:

            return JsonResponse({'result': 'false', 'response':"Please Insert valid data"}, safe=False)


class PlanGetView(GenericAPIView):
    serializer_class = PlanViewSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    
    @swagger_auto_schema(tags=['Subscribe Plans'])
    def get(self,request):
        serializer_class=PlanViewSerializer(data=request.data)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # import pdb;pdb.set_trace()
            obj=Plans.objects.all()
            plan_feature=PlanFeatures.objects.all()
            prices = stripe.Price.list().data
            product = []
            for price in prices:
                prod=stripe.Product.retrieve(price['product'],)
                # print(prod)
                # import pdb;pdb.set_trace()
                product.append({'product_id':prod['id'],'product_name':prod['name'],'price_id':price['id'], 'lookup_key':price['lookup_key'],
                    'currency':price['currency'],'unit_amount':(price['unit_amount']), 'interval':price['recurring']['interval']})
                a,_=Plans.objects.get_or_create(product_id=prod['id'],name=prod['name'],price_id=price['id'], lookup_key=price['lookup_key'],
                    currency=price['currency'],price=(price['unit_amount']), interval=price['recurring']['interval'])
            # print(product)

        except:
            return JsonResponse({'result':'false','response':'Something went wrong, Please check.'})

        # a = price.data
        # print(a.id)
        return JsonResponse({'result':'true','Local Database':PlanViewSerializer(obj,many=True).data,'Stripe Data':product},safe=False)


class PaymentSuccessView(APIView):
    # serializer_class = PlanViewSerializer
    # permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (TokenAuthentication,)
    
    @swagger_auto_schema(tags=['Subscribe Plans'])
    def get(self,request):
        # import pdb;pdb.set_trace()
        try:
            checkout_session_id = request.GET.get('session_id')
            redirect_url = request.GET.get('redirect_url')
            usermail = request.GET.get('useremail')
            # print(usermail)
            checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)
            session_id = checkout_session.id
            amount_submitted = checkout_session['amount_subtotal']
            total_amount = checkout_session['amount_total']
            cancel_url = ' '
            currency = checkout_session['currency']
            customer = checkout_session['customer']
            customer_email = checkout_session['customer_details']['email']
            customer_phone = checkout_session['customer_details']['phone']
            expiry_date1 = checkout_session['expires_at']
            payment_mode = checkout_session['mode']
            payment_status = checkout_session['payment_status']
            status = checkout_session['status']
            subscription_id = checkout_session['subscription']
            success_url = checkout_session['success_url']
            ts = int(expiry_date1)
            expiry_date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')

            SubscriptionPayment.objects.update_or_create(session_id=session_id,amount_submitted=amount_submitted,total_amount=total_amount,cancel_url=cancel_url,currency=currency,
            customer=customer,customer_email=customer_email,customer_phone=customer_phone,expiry_date=expiry_date,payment_mode=payment_mode,payment_status=payment_status
            , status=status, subscription_id=subscription_id,success_url=success_url)
            
            subscription1=stripe.Subscription.retrieve(checkout_session['subscription'],)
            plan_price_id = subscription1['plan']['id']
            plan_for_user_subscription = Plans.objects.get(price_id = plan_price_id) # plan
            
            plan_feature = PlanFeatures.objects.filter(plans = plan_for_user_subscription.id)
            print(plan_feature)
            print(plan_for_user_subscription.name)
            dict1 = {}
            for p in plan_feature:
                dict1.update({p.name : p.Value})
            # import pdb;pdb.set_trace()
            print(dict1)  
            user = User.objects.get(email=usermail)
            planexit = PlansFeatureUser.objects.filter(user=user).count()
            print(planexit)
            if planexit == 0:
                print("data null hai")
                PlansFeatureUser.objects.create(user= user, plans= plan_for_user_subscription, ConcurrentHTTP=dict1["ConcurrentHTTP"],ConcurrentBrowsers=dict1["ConcurrentBrowsers"],
                HTTPUserHours=dict1['HTTPUserHours'],BrowserUserHours=dict1['BrowserUserHours'],LoadInjectorHours=dict1['LoadInjectorHours'],
                Max_Test_Duration_per_test=int(dict1['Max_Test_Duration_per_test']),UnusedResourceRollover=dict1['UnusedResourceRollover'],expiry_date=expiry_date)
            else:
                print("data is not null")
                PlansFeatureUser.objects.create(user= user, plans= plan_for_user_subscription, ConcurrentHTTP=dict1["ConcurrentHTTP"],ConcurrentBrowsers=dict1["ConcurrentBrowsers"],
                HTTPUserHours=dict1['HTTPUserHours'],BrowserUserHours=dict1['BrowserUserHours'],LoadInjectorHours=dict1['LoadInjectorHours'],
                Max_Test_Duration_per_test=int(dict1['Max_Test_Duration_per_test']),UnusedResourceRollover=dict1['UnusedResourceRollover'],expiry_date=expiry_date,status=False)

        except:  
            return JsonResponse({'result':'false','response':'Something went wrong, Please check.'})

        return HttpResponseRedirect(redirect_url)



class PaymentFailView(APIView):
    # permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (TokenAuthentication,)
    
    @swagger_auto_schema(tags=['Subscribe Plans'])
    def get(self,request):
        try:
            checkout_session_id = request.GET.get('session_id')
            redirect_url = request.GET.get('redirect_url')
            checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)
            
            session_id = checkout_session.id
            amount_submitted = checkout_session['amount_subtotal']
            total_amount = checkout_session['amount_total']
            cancel_url = checkout_session['cancel_url']
            currency = checkout_session['currency']
            customer = checkout_session['customer']
            customer_email = checkout_session['customer_details']['email']
            customer_phone = checkout_session['customer_details']['phone']
            expiry_date = checkout_session['expires_at']
            payment_mode = checkout_session['mode']
            payment_status = checkout_session['payment_status']
            status = checkout_session['status']
            subscription_id = checkout_session['subscription']
            success_url = ' '

            # import pdb;pdb.set_trace()
            SubscriptionPayment.objects.update_or_create(session_id=session_id,amount_submitted=amount_submitted,total_amount=total_amount,cancel_url=cancel_url,currency=currency,
            customer=customer,customer_email=customer_email,customer_phone=customer_phone,expiry_date=expiry_date,payment_mode=payment_mode,payment_status=payment_status
            , status=status, subscription_id=subscription_id,success_url=success_url)


        except:  
            return JsonResponse({'result':'false','response':'Something went wrong, Please check.'})

        return HttpResponseRedirect(redirect_url)