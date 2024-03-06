from .models import *
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserChangeForm
from django.forms import formset_factory


def positive_int_validator(value):
    try:
        assert int(value) >= 0
    except (AssertionError, ValueError):
        raise ValidationError('The value must be a positive integer')


def validate_file_size(value):
    # 2 MB is equivalent to 2 * 1024 * 1024 bytes
    max_size = 2 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError('File size cannot exceed 2 MB.')


# (YYYY-MM-DD)
date_validator = RegexValidator(
    regex='^\d{4}-\d{2}-\d{2}$',
    message='Invalid date format. Use YYYY-MM-DD format.',
)


class ProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_photo',)


class KeywordForm(forms.Form):
    name = forms.CharField(
        label='Keyword',
        required=False
    )
    value_after = forms.CharField(
        label='Date After',
        required=False,
        validators=[date_validator]
    )
    value_before = forms.CharField(
        label='Date Before',
        required=False,
        validators=[date_validator]
    )
    channel_name = forms.CharField(
        label='Channel Name',
        required=False
    )


class SearchVideoForm(forms.Form):
    query = forms.CharField()
    search_by = forms.ChoiceField(
        label='Search by',
        label_suffix='',
        choices=[('keyword', 'Keyword'), ('channel_id', 'Channel id')],
        widget=forms.Select(attrs={
            'class': 'dropdown__input_hidden',
            'name': 'select-category',
        }),
        initial='Keyword',
    )
    date_after = forms.CharField(
        label='Date after',
        label_suffix='',
        validators=[date_validator]
    )
    date_before = forms.CharField(
        label='Date before',
        label_suffix='',
        validators=[date_validator]
    )
    country_code = forms.ChoiceField(
        label='Country',
        label_suffix='',
        choices=[
            ('All', 'All'),
            ('AE', 'United Arab Emirates'),
            ('AF', 'Afghanistan'),
            ('AL', 'Albania'),
            ('AR', 'Argentina'),
            ('AT', 'Austria'),
            ('AU', 'Australia'),
            ('AZ', 'Azerbaijan'),
            ('BA', 'Bosnia and Herzegovina'),
            ('BD', 'Bangladesh'),
            ('BE', 'Belgium'),
            ('BG', 'Bulgaria'),
            ('BH', 'Bahrain'),
            ('BO', 'Bolivia'),
            ('BR', 'Brazil'),
            ('BY', 'Belarus'),
            ('CA', 'Canada'),
            ('CH', 'Switzerland'),
            ('CL', 'Chile'),
            ('CO', 'Colombia'),
            ('CR', 'Costa Rica'),
            ('CY', 'Cyprus'),
            ('CZ', 'Czech Republic'),
            ('DE', 'Germany'),
            ('DK', 'Denmark'),
            ('DO', 'Dominican Republic'),
            ('DZ', 'Algeria'),
            ('EC', 'Ecuador'),
            ('EE', 'Estonia'),
            ('EG', 'Egypt'),
            ('ES', 'Spain'),
            ('FI', 'Finland'),
            ('FR', 'France'),
            ('GB', 'United Kingdom'),
            ('GE', 'Georgia'),
            ('GH', 'Ghana'),
            ('GR', 'Greece'),
            ('GT', 'Guatemala'),
            ('HK', 'Hong Kong'),
            ('HN', 'Honduras'),
            ('HR', 'Croatia'),
            ('HU', 'Hungary'),
            ('ID', 'Indonesia'),
            ('IE', 'Ireland'),
            ('IL', 'Israel'),
            ('IN', 'India'),
            ('IS', 'Iceland'),
            ('IT', 'Italy'),
            ('JM', 'Jamaica'),
            ('JP', 'Japan'),
            ('KE', 'Kenya'),
            ('KH', 'Cambodia'),
            ('KR', 'South Korea'),
            ('KW', 'Kuwait'),
            ('LA', 'Laos'),
            ('LB', 'Lebanon'),
            ('LK', 'Sri Lanka'),
            ('LT', 'Lithuania'),
            ('LU', 'Luxembourg'),
            ('LV', 'Latvia'),
            ('LY', 'Libya'),
            ('MA', 'Morocco'),
            ('ME', 'Montenegro'),
            ('MK', 'North Macedonia'),
            ('MT', 'Malta'),
            ('MX', 'Mexico'),
            ('MY', 'Malaysia'),
            ('NG', 'Nigeria'),
            ('NI', 'Nicaragua'),
            ('NL', 'Netherlands'),
            ('NO', 'Norway'),
            ('NP', 'Nepal'),
            ('NZ', 'New Zealand'),
            ('PA', 'Panama'),
            ('PE', 'Peru'),
            ('PG', 'Papua New Guinea'),
            ('PH', 'Philippines'),
            ('PK', 'Pakistan'),
            ('PL', 'Poland'),
            ('PR', 'Puerto Rico'),
            ('PT', 'Portugal'),
            ('PY', 'Paraguay'),
            ('QA', 'Qatar'),
            ('RO', 'Romania'),
            ('RS', 'Serbia'),
            ('RU', 'Russia'),
            ('SA', 'Saudi Arabia'),
            ('SE', 'Sweden'),
            ('SG', 'Singapore'),
            ('SI', 'Slovenia'),
            ('SK', 'Slovakia'),
            ('SN', 'Senegal'),
            ('SV', 'El Salvador'),
            ('TH', 'Thailand'),
            ('TN', 'Tunisia'),
            ('TR', 'Turkey'),
            ('TW', 'Taiwan'),
            ('TZ', 'Tanzania'),
            ('UA', 'Ukraine'),
            ('UG', 'Uganda'),
            ('US', 'United States'),
            ('UY', 'Uruguay'),
            ('VE', 'Venezuela'),
            ('VN', 'Vietnam'),
            ('ZA', 'South Africa'),
            ('ZW', 'Zimbabwe')
        ],
        # Додайте решту кодів країн за потреби
        widget=forms.Select(attrs={
            'class': 'dropdown__input_hidden',
            'name': 'select-country',
        }),
    )
    shorts = forms.BooleanField(
        label='Shorts',
        required=False,  # Опційне поле, вибір за бажанням
    )


class SearchChannelsForm(forms.Form):
    query = forms.CharField()
    country = forms.ChoiceField(
        label='Country code',
        label_suffix='',
        choices=(
                [('all', 'All countries')] +
                [(country.code, country.name) for country in Country.objects.all()]
        ),
        widget=forms.Select(attrs={
            'class': 'dropdown__input_hidden',
            'name': 'select-category',
        }),
        initial='All countries',
    )
    # top bound
    less_than = forms.IntegerField(
        label='Top bound',
        label_suffix='',
        required=False,
        validators=[positive_int_validator]
    )
    # bottom bound
    more_than = forms.IntegerField(
        label='Bottom bound',
        label_suffix='',
        required=False,
        validators=[positive_int_validator]
    )

    def clean_country(self):
        if self.cleaned_data['country'] == 'all':
            self.cleaned_data['country'] = None

        return self.cleaned_data['country']

    def clean(self):
        invalid_subscribers_range = (
                self.cleaned_data['more_than'] is not None and
                self.cleaned_data['less_than'] is not None and
                self.cleaned_data['more_than'] > self.cleaned_data['less_than']
        )
        if invalid_subscribers_range:
            raise ValidationError(
                '"Less than" value must be greater than "More than" value'
            )

        return self.cleaned_data


class FeedBackForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    category = forms.ChoiceField(
        choices=[('payment', 'Payment'), ('service', 'Service functionality'), ('general', 'General questions'),
                 ('errors', 'Errors and bugs report'), ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        initial='general',
        label='What kind of question you have?',
    )
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-input'}))


class AddDealForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'add-deal__input add-deal__input-calendar-btn', 'type': 'text'}),
        # input_formats=[r'%d/%m/%y'],
    )
    brand = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'add-deal__input', 'type': 'text', 'placeholder': 'Enter Brand'}),
        required=True,
        max_length=100,
    )
    status = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'add-deal__input', 'type': 'text', 'placeholder': 'Enter Status'}),
        max_length=100,
        required=False,
    )
    name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'add-deal__input', 'placeholder': 'Enter a brand Name...'})
    )
    email = forms.EmailField(
        max_length=255,
        required=False,
        widget=forms.EmailInput(attrs={'class': 'add-deal__input', 'placeholder': 'Enter contact Email...'})
    )
    phone_number = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'add-deal__input', 'placeholder': 'Enter Contact Phone...'})
    )
    rated_quoted = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'add-deal__input', 'placeholder': 'Rated Quoted'})
    )
    counter_offer = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'add-deal__input', 'placeholder': 'Counter Offer'})
    )
    agreed_rate = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'add-deal__input', 'placeholder': 'Agreed Rate'})
    )
    introduction = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
        required=False,
        initial=True,
    )
    pitch = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'add-deal__input'}),
        required=False,
        initial=True,
    )
    views_impressions = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'add-deal__input', 'id': 'viewsImpressionsCheckbox'}),
        required=False,
        initial=True,
    )
    views_amount = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'add-deal__input viewsAmountField',
                                      'placeholder': 'Amount of views',
                                      'id': 'viewsAmountField',
                                      }),
        label="Amount"
    )
    affiliate_check = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'add-deal__input', 'id': 'affiliateCheckbox'}),
        required=False,
        initial=True,
    )
    affiliate_link = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'add-deal__input',
                                      'placeholder': 'Enter Affiliate link',
                                      'id': 'affiliateLinkField',
                                      }),
        label="Affiliate link"
    )
    commissions = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'add-deal__input',
                                      'placeholder': 'Enter commission',
                                      'id': 'commissionsField',
                                      }),
        label="Commissions %"
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'add-deals-platforms-comments__textarea'})
    )

    users_found_deal = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'add-deal__input',
                                      'placeholder': 'Enter users_found_deal',
                                      'id': 'users_found_deal',
                                      }),
        label="users found deal"
    )

    class Meta:
        model = DealInfo
        fields = '__all__'


class DocumentForm(forms.ModelForm):
    docfile = forms.FileField(validators=[validate_file_size], widget=forms.ClearableFileInput(attrs={'class': 'formset-file'}))

    class Meta:
        model = Document
        fields = '__all__'


class InvoiceForm(forms.Form):
    logo = forms.ImageField(required=False)
    invoice_from = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.Textarea(attrs={'class': 'add-deal__input',
                                     'placeholder': 'Who is this invoice to? (required)',
                                     'rows': 1,
                                     }),
    )
    bill_to = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.Textarea(attrs={'class': 'add-deal__input',
                                     'placeholder': 'Who is this invoice to? (required)',
                                     'rows': 1,
                                     }),
    )
    ship_to = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={'class': 'add-deal__input',
                                     'placeholder': '(optional)',
                                     'rows': 1,  # По замовчуванню 1 рядок
                                     }),
    )
    invoice_tag = forms.CharField(
        max_length=255,
        initial='1',
        widget=forms.TextInput(attrs={'class': 'add-deal__input',
                                      'type': 'text'}),
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'add-deal__input add-deal__input-calendar-btn'}),
        input_formats=[r'%d/%m/%y'],
        required=False,
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'add-deal__input add-deal__input-calendar-btn', 'type': 'text'}),
        input_formats=[r'%d/%m/%y'],
        required=False,
    )
    payment_terms = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'add-deal__input',
                                      'type': 'text'}),
    )
    po_number = forms.CharField(max_length=255,
                                required=False,
                                widget=forms.TextInput(attrs={'class': 'add-deal__input',
                                                              'type': 'text'}), )

    notes = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={'class': 'add-deal__input',
                                     'placeholder': 'Notes - any relevant information not already covered',
                                     'rows': 1,  # По замовчуванню 1 рядок
                                     }),
    )
    terms = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'add-deal__input',
            'placeholder': 'Terms and conditions - late fees, payment methods, delivery schedule',
            'rows': 1,  # По замовчуванню 1 рядок
        }),
    )
    discount = forms.FloatField(
        initial=0,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'add-deal__input',
            'type': 'number'}),
    )
    discount_changer = forms.BooleanField(required=False)
    shipping = forms.FloatField(
        initial=0,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'add-deal__input',
            'type': 'number'}),
    )
    tax = forms.FloatField(
        initial=0,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'add-deal__input',
            'type': 'number'}),
    )
    tax_changer = forms.BooleanField(required=False)
    amount_paid = forms.FloatField(
        initial=0,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'add-deal__input',
            'type': 'number'}),
    )


class ItemForm(forms.Form):
    item_description = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'add-deal__input',
                                      'placeholder': 'Description of service or product...',
                                      'type': 'text',
                                      }),
    )
    quantity = forms.IntegerField(
        initial=1,
        widget=forms.TextInput(attrs={'class': 'add-deal__input',
                                      'type': 'number',
                                      }),
    )
    rate = forms.FloatField(
        initial=0,
        widget=forms.TextInput(attrs={'class': 'add-deal__input',
                                      'type': 'text',
                                      }),
    )


# ItemFormSet = formset_factory(ItemForm, extra=1, can_delete=True, can_delete_extra=True)
ItemFormSet = formset_factory(ItemForm, extra=1)
DocumentFormSet = formset_factory(DocumentForm, extra=5)
