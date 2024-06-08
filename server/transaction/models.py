from django.db import models
from user.models import User

# Create your models here.


Interval_plan = (
    ('Month','month'),
    ('Year', 'year')
)

class Plans(models.Model):
    name = models.CharField(max_length=70,verbose_name='Subscription Name')
    price = models.FloatField(verbose_name='Price')
    interval = models.CharField(max_length=20, choices=Interval_plan, default='Month')
    product_id = models.CharField(max_length=200)
    price_id = models.CharField(max_length=200)
    lookup_key = models.CharField(max_length=200)
    currency = models.CharField(max_length=200)
    def __str__(self):
        return self.name


class PlanFeatures(models.Model):
    name = models.CharField(max_length=200)
    type = models.BooleanField(max_length=200)
    Value = models.CharField(max_length=500)
    plans = models.ManyToManyField(Plans,related_name='features')


class Subscription(models.Model):
    user = models.ForeignKey(to=User,verbose_name='UserProfile',on_delete=models.PROTECT)
    user_email = models.EmailField()
    plans = models.ForeignKey(to=Plans,verbose_name='Plans',on_delete=models.PROTECT)
    price_id = models.CharField(max_length=500)
    session_id = models.CharField(max_length=500)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

class PlansFeatureUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    plans = models.ForeignKey(Plans, on_delete=models.CASCADE)
    ConcurrentHTTP = models.CharField(max_length=150)
    ConcurrentBrowsers = models.CharField(max_length=150)
    HTTPUserHours = models.CharField(max_length=150)
    BrowserUserHours = models.CharField(max_length=150)
    LoadInjectorHours = models.CharField(max_length=150)
    Max_Test_Duration_per_test = models.FloatField()
    UnusedResourceRollover = models.CharField(max_length=150)
    expiry_date = models.CharField(max_length=100)
    status = models.BooleanField(default=True)


class SubscriptionUsed(models.Model):
    user = models.ForeignKey(to=User,verbose_name='UserProfile',on_delete=models.PROTECT)
    subscription = models.ForeignKey(to=Subscription,verbose_name='subscription',on_delete=models.PROTECT)
    total_no_of_test = models.IntegerField()
    no_of_test_perform = models.IntegerField(default=0)
    test_duration = models.CharField(max_length=500)
    remaining_test = models.IntegerField()
    no_of_user = models.IntegerField()
    feature = models.ManyToManyField(PlanFeatures)

class SubscriptionPayment(models.Model):
    session_id = models.CharField(max_length=300, null=True,blank=True)
    amount_submitted = models.IntegerField(null=True,blank=True)
    total_amount = models.IntegerField(null=True,blank=True)
    cancel_url = models.CharField(max_length=300, null=True,blank=True)
    currency = models.CharField(max_length=300, null=True,blank=True)
    customer = models.CharField(max_length=300, null=True,blank=True)
    customer_email = models.CharField(max_length=300, null=True,blank=True)
    customer_phone = models.CharField(max_length=300, null=True,blank=True)
    expiry_date = models.CharField(max_length=300, null=True,blank=True)
    payment_mode = models.CharField(max_length=300, null=True,blank=True)
    payment_status = models.CharField(max_length=300, null=True,blank=True)
    status = models.CharField(max_length=300, null=True,blank=True)
    subscription_id = models.CharField(max_length=300, null=True,blank=True)
    success_url = models.CharField(max_length=300, null=True,blank=True)