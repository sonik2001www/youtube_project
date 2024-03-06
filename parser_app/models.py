from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator


class Country(models.Model):
    code = models.CharField('Country code', max_length=10, unique=True)
    name = models.CharField('Name', max_length=250)
    flag = models.ImageField('Flag', upload_to='flag', blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField('Name', max_length=250)
    domain = models.CharField('Domain', max_length=250)
    logo = models.ImageField('Logo', upload_to='brand', blank=True, null=True)
    key_people = models.CharField('Key people', max_length=250, blank=True)
    industries = ArrayField(
        models.CharField(max_length=250),
        verbose_name='Industries',
        blank=True
    )
    country = models.ForeignKey(
        'parser_app.Country',
        verbose_name='Country',
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        required_db_vendor = 'postgresql'

    def __str__(self):
        return self.name


class Quota(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    requests = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Quota'
        verbose_name_plural = 'Quotas'

    def __str__(self):
        return self.name
  

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile', blank=True, null=True)
    video_requests = models.BigIntegerField(default=0)
    channel_requests = models.BigIntegerField(default=0)
    search_requests = models.BigIntegerField(default=0)
    total_requests = models.BigIntegerField(default=0)
    quota = models.ForeignKey(
        Quota,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    payment = models.BooleanField(default=False)
    plan_start = models.DateTimeField(null=True, blank=True)
    plan_expired_on = models.DateTimeField(null=True, blank=True)
    plan_expired = models.BooleanField(default=False)
    
    plan_availiable_requests = models.IntegerField(default=0)
    temp_token = models.CharField(max_length=255, null=True, blank=True)
  

class Channel(models.Model):
    channel_id = models.CharField(max_length=100)
    title = models.CharField(max_length=250, blank=True, null=True)
    url = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    description = models.TextField()
    published = models.DateTimeField(blank=True, null=True)
    # list websites are taken from the description of the channel
    websites_list = ArrayField(models.CharField(max_length=250), blank=True)
    subscribers_count = models.IntegerField(blank=True, null=True)
    video_count = models.IntegerField(blank=True, null=True)
    youtube_categories = ArrayField(models.CharField(max_length=250), blank=True)
    thumbnail_medium_url = models.CharField(max_length=150, blank=True, null=True)
    country = models.ForeignKey(
        'parser_app.Country',
        on_delete=models.PROTECT,
        null=True
    )
    users_found_channel = models.ManyToManyField(Profile)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id']
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'
        required_db_vendor = 'postgresql'

    def get_absolute_url(self):
        return reverse(
            'creator_overview',
            kwargs={'channel_id': self.channel_id}
        )

    @property
    def categories(self) -> str:
        return ', '.join(self.youtube_categories)


class Video(models.Model):
    video_id = models.CharField(max_length=100)
    channel_id = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=250, null=True, blank=True)
    # list websites are taken from the description of the video
    websites_list = ArrayField(models.CharField(max_length=250), null=True, blank=True)
    published = models.DateTimeField(null=True, blank=True)
    url = models.CharField(max_length=250, null=True, blank=True)
    views_count = models.IntegerField(blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=250), null=True, blank=True)
    thumbnail_medium_url = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=25, default='New')

    users_found_video = models.ManyToManyField(Profile)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
        required_db_vendor = 'postgresql'

    def channel_subscribers_count(self):
        try:
            return Channel.objects.filter(channel_id=self.channel_id)[0].subscribers_count
        except Channel.DoesNotExist:
            return None

    def channel_country(self):
        try:
            return (
                Channel.objects.filter(channel_id=self.channel_id)[0].country or
                'Country unknown'
            )
        except Channel.DoesNotExist:
            return None




class Remove(models.Model):
    name = models.CharField(max_length=100)

    users_found_remove = models.ManyToManyField(Profile)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Remove'
        verbose_name_plural = 'Remove'


class Keyword(models.Model):
    name = models.CharField(max_length=250)
    status = models.CharField(max_length=25, default='New')

    users_found_keyword = models.ManyToManyField(Profile)
    next_page_token = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Keyword'
        verbose_name_plural = 'Keywords'


class Settings(models.Model):
    name = models.CharField(max_length=250, unique=True)
    value = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Settings'
        verbose_name_plural = 'Settings'


class Document(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    docfile = models.FileField(upload_to='media/documents/')

    def __str__(self):
        return self.title


class DealInfo(models.Model):
    brand = models.CharField(max_length=255)
    date = models.DateField()
    status = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)
    rated_quoted = models.CharField(max_length=255)
    counter_offer = models.CharField(max_length=255)
    agreed_rate = models.CharField(max_length=255)
    introduction = models.BooleanField(default=False)
    pitch = models.BooleanField(default=False)
    views_impressions = models.BooleanField(default=False)
    views_amount = models.CharField(max_length=255, null=True, blank=True)
    affiliate_check = models.BooleanField(default=False)
    affiliate_link = models.CharField(max_length=255, null=True, blank=True)
    commissions = models.CharField(max_length=255, null=True, blank=True)
    archive = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)
    document = models.ManyToManyField('Document', blank=True)

    users_found_deal = models.ManyToManyField(Profile)


#######################################################################
# SALES #


class DrugAndDoorField(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    price = models.CharField(max_length=30, null=True, blank=True)
    drug_and_door_col = models.ForeignKey('DrugAndDoorCol', related_name='fields', blank=True, null=True, on_delete=models.CASCADE)
    position = models.IntegerField(null=True, blank=True)
    STARS_CHOICES = [(0, '0'), (1, '1'), (2, '2'), (3, '3')]
    stars = models.IntegerField(choices=STARS_CHOICES, null=True, blank=True, default=0)

    users_found_pipeline = models.ManyToManyField(Profile)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Drug And Door Field'
        verbose_name_plural = 'Drug And Door Fields'


class DrugAndDoorCol(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)

    users_found_pipeline = models.ManyToManyField(Profile)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Drug And Door Col'
        verbose_name_plural = 'Drug And Doors Col'

    def order_by_field(self):
        return self.fields.order_by('position')




