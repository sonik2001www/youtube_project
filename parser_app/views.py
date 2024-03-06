import requests, os, tempfile, mimetypes, pdfkit, stripe, secrets
from paypalrestsdk import Payment, set_config
from parser_app import forms
from parser_app import models
from parser_app.modules import parser, gmail_sender
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse, FileResponse
from django.conf import settings
from datetime import timedelta


def pars(request):
    return render(request, 'dashboard.html', {'username': request.user.username})


@login_required
def user_profile(request):
    
    #######################################################################################################
    # fix an error : django.contrib.auth.models.User.profile.RelatedObjectDoesNotExist: User has no profile.
    # from django.contrib.auth.models import User
    try:
        profile = request.user.profile
        quota = profile.quota
        if not quota:
            quota = models.Quota.objects.get(name='default')
            profile.quota = quota
            profile.save()
    except User.profile.RelatedObjectDoesNotExist:
        # Create a profile for the user if it doesn't exist
        profile = models.Profile.objects.create(user=request.user)
        quota = models.Quota.objects.get(name='default')
        profile.quota = quota
        profile.save()
    #########################################################################################################

    if request.method == 'GET':
        quota_id = request.GET.get('quota_id')
        if quota_id:
            quota = models.Quota.objects.get(pk=quota_id)
            profile.quota = quota
            profile.save()
            messages.success(request, 'Your plan and quota have been successfully changed...')
            return redirect('user_profile') 

    username = request.user.username
    email = request.user.email
    date_joined = request.user.date_joined
    quota = request.user.profile.quota

    video_requests = profile.video_requests
    search_requests = profile.search_requests
    channel_requests = profile.channel_requests
    total_requests = profile.total_requests
    plan_start = profile.plan_start
    plan_expired_on = profile.plan_expired_on
    plan_limit = quota.requests
    plan_availiable_requests = profile.plan_availiable_requests
    plan_status = profile.payment

    if plan_start:
        plan_remaining_time = plan_expired_on - timezone.now()

        # sending an email if plan has allready expired or 3 (or less) days left
        writer = gmail_sender.GmailSender()

        if timedelta(seconds=1) > plan_remaining_time:
            profile.plan_expired = True
            profile.save()
            writer.send_plan_expired_warning(receiver=email)
        elif plan_remaining_time >= timedelta(days=3):
            writer.send_plan_3days_warning(receiver=email)
    else:
        plan_remaining_time = 'undefined'

    if request.method == 'POST':
        form = forms.ProfilePhotoForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = forms.ProfilePhotoForm(instance=profile)

    context = {
        'username': username,
        'email': email,
        'date_joined': date_joined,
        'quota': quota,
        'form': form,
        'video_requests': video_requests,
        'search_requests': search_requests,
        'channel_requests': channel_requests,
        'total_requests': total_requests,
        'plan_start': plan_start,
        'plan_expired_on': plan_expired_on,
        'plan_remaining_time': plan_remaining_time,
        'plan_status': plan_status,
        'plan_limit': plan_limit,
        'plan_availiable_requests': plan_availiable_requests, 
    }
    return render(request, 'account.html', context)


@login_required
def load_videos(request, limit: int, offset: int):
    profile = request.user.profile
    videos_obj = models.Video.objects.filter(users_found_video=profile)

    if len(videos_obj) == offset:
        key = models.Keyword.objects.filter(users_found_keyword=profile).latest('id')

        if not request.user.profile.payment:
            messages.warning(request, 'Your plan is not payed, pay your plan to access requests...')
            return redirect('user_profile')
        elif request.user.profile.plan_expired:
            request.user.profile.plan_availiable_requests = 0
            request.user.profile.save()
            messages.warning(request, 'Your plan is expired, renew your plan to access requests...')
            return redirect('user_profile')
        elif 'limit' == parser.search_videos(user_id=request.user.id, page_token=key.next_page_token) or 'limit' == parser.add_video_data(user_id=request.user.id):
            messages.warning(request, 'Your requests quota has exhausted, upgrade your plan to increase your requests limits...')
            return redirect('pricing')
        print('\n\n\n-----------ok--------\n\n\n')

    print(offset+limit)
    videos = models.Video.objects.filter(users_found_video=profile).order_by('id')[offset: offset+limit]
    if (len(videos) == 0):
        return HttpResponseNotFound()

    return render(request, 'layouts/videos_cycle.html', {'videos': videos})


@login_required
def video_output(request):
    date_after = models.Settings.objects.get(name='Date After')
    date_before = models.Settings.objects.get(name='Date Before')
    form = forms.SearchVideoForm()
    profile = request.user.profile
    removes = models.Remove.objects.filter(users_found_remove=profile)
    country_code = models.Settings.objects.get(name='Country')
    shorts = models.Settings.objects.get(name='Shorts')

    if request.method == 'POST':
        form = forms.SearchVideoForm(request.POST)
        print(form.is_valid(), '- form.is_valid()')
        if form.is_valid():
            if form.cleaned_data['search_by'] == 'channel_id':
                channel_value = form.cleaned_data['query']
                keyword_value = ''
            else:
                channel_value = ''
                keyword_value = form.cleaned_data['query']
            obj = models.Keyword.objects.create(name=keyword_value)
            created = True
            obj.users_found_keyword.add(profile)


            # Оновлення значень полів у поточному екземплярі форми
            form.cleaned_data['country_code'] = form.cleaned_data['country_code']
            form.cleaned_data['shorts'] = form.cleaned_data['shorts']

            channel = models.Settings.objects.get(name='Channel Name')
            channel.value = channel_value
            channel.save()

            date_after.value = form.cleaned_data['date_after']
            date_after.save()

            date_before.value = form.cleaned_data['date_before']
            date_before.save()

            country_code.value = form.cleaned_data['country_code']
            country_code.save()

            shorts.value = form.cleaned_data['shorts']
            shorts.save()

            if not request.user.profile.payment:
                messages.warning(request, 'Your plan is not payed, pay your plan to access requests...')
                return redirect('user_profile')
            elif request.user.profile.plan_expired:
                request.user.profile.plan_availiable_requests = 0
                request.user.profile.save()
                messages.warning(request, 'Your plan is expired, renew your plan to access requests...')
                return redirect('user_profile')
            elif 'limit' == parser.search_videos(user_id=request.user.id) or 'limit' == parser.add_video_data(user_id=request.user.id):
                messages.warning(request, 'Your requests quota has exhausted, upgrade your plan to increase your requests limits...')
                return redirect('pricing')
            else:
                parser.remove_websites()
                return redirect('video_output')

    context = {
        'username': request.user.username,
        'videos': models.Video.objects.filter(users_found_video=profile).order_by('id')[:15],
        'form': form,
        'date_after': date_after.value,
        'date_before': date_before.value,
        'country_code': country_code,
        'shorts': shorts,
        'removes': removes,
    }
    return render(request, 'videos.html', context)


def remove_item(request, rem):
    profile = request.user.profile
    # Отримання запису за допомогою remove_id та видалення його з бази даних
    try:
        rem = models.Remove.objects.get(name=rem, users_found_remove=profile)
        rem.delete()
        return JsonResponse({'message': 'Item removed successfully.'})
    except models.Remove.DoesNotExist:
        return JsonResponse({'error': 'Item not found.'}, status=404)


@login_required
def load_channels(request, limit: int, offset: int):
    profile = request.user.profile
    channels = models.Channel.objects.filter(users_found_channel=profile).select_related('country').order_by('id')[offset : offset+limit]
    if (len(channels) == 0):
        return HttpResponseNotFound()

    return render(request, 'layouts/channels_cycle.html', {'channels': channels})


@login_required
def channels_output(request):
    form = forms.SearchChannelsForm()
    profile = request.user.profile

    if request.method == 'POST':
        form = forms.SearchChannelsForm(request.POST)
        if form.is_valid():
            if not request.user.profile.payment:
                    messages.warning(request, 'Your plan is not payed, pay your plan to access requests...')
                    return redirect('user_profile')
            elif request.user.profile.plan_expired:
                request.user.profile.plan_availiable_requests = 0
                request.user.profile.plan_availiable_requests.save()
                messages.warning(request, 'Your plan is expired, renew your plan to access requests...')
                return redirect('user_profile')
            elif 'limit' == parser.search_channels(
                user_id=request.user.id,
                query=form.cleaned_data['query'],
                less_than=form.cleaned_data['less_than'],
                more_than=form.cleaned_data['more_than'],
                country_code=form.cleaned_data['country'],
            ):
                messages.warning(request, 'Your requests quota has exhausted, upgrade your plan to increase your limit...')
                return redirect('pricing')
            else:
                return redirect('channels_output')

    context = {
        'username': request.user.username,
        'channels': models.Channel.objects.filter(users_found_channel=profile).select_related('country').order_by('id')[:4],
        'form': form
    }
    return render(request, 'channels.html', context)


@login_required
def tools(request):
    return render(request, 'tools.html', {'username': request.user.username})


@login_required
def creator_overview(request, channel_id: str):
    try:
        channel = models.Channel.objects.filter(channel_id=channel_id)[0]
    except:
        return HttpResponseNotFound()
    print(channel)
    brands = set()
    for video in models.Video.objects.filter(channel_id=channel_id):
        for brand in models.Brand.objects.all():
            sites = ' '.join(video.websites_list)
            print(brand.domain, '\n', sites)
            if brand.domain.split('.', maxsplit=1)[1] in sites:
                brands.add(brand)

    context = {
        'username': request.user.username,
        'channel': channel,
        'brands': brands,
    }
    return render(request, 'creator-overview.html', context)


@login_required
def libary_search(request, sort_field):
    try:
        size = int(request.GET.get('size'))
        assert size > 0
    except:
        size = 15

    try:
        page_number = int(request.GET.get('page'))
        assert page_number > 0
    except:
        page_number = 1

    queryset = models.Brand.objects.all()

    # set default sort method 
    if not sort_field:
        sort_field = 'name'

    queryset = models.Brand.objects.all().order_by(sort_field)
    paginator = Paginator(queryset, size)

    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return redirect('libary_search')

    username = request.user.username
    count = models.Brand.objects.all().count()
    start = (page_number - 1)*size + 1
    end = page_number*size if count > page_number*size else count

    return render(request, 'libary-search.html', locals())


@login_required
def pricing(request):
    context = {
        'username': request.user.username,
        'low_quota': models.Quota.objects.get(name='Low'),
        'medium_quota': models.Quota.objects.get(name='Medium'),
        'pro_quota': models.Quota.objects.get(name='Pro'),
    }
    return render(request, 'pricing.html', context)


@login_required
def search(request):
    if request.method == 'POST':
        if not request.user.profile.payment:
                messages.warning(request, 'Your plan is not payed, pay your plan to access requests...')
                return redirect('user_profile')
        elif request.user.profile.plan_expired:
            request.user.profile.plan_availiable_requests = 0
            request.user.profile.plan_availiable_requests.save()
            messages.warning(request, 'Your plan is expired, renew your plan to access requests...')
            return redirect('user_profile')
        elif 'limit' == parser.search_videos(user_id=request.user.id):
            messages.warning(request, 'Your requests quota has exhausted, upgrade your plan to increase your limit...')
            return redirect('pricing')
        else:
            return redirect('pars')


def check(request):
    if request.method == 'POST':
        if not request.user.profile.payment:
                messages.warning(request, 'Your plan is not payed, pay your plan to access requests...')
                return redirect('user_profile')
        elif request.user.profile.plan_expired:
            request.user.profile.plan_availiable_requests = 0
            request.user.profile.plan_availiable_requests.save()
            messages.warning(request, 'Your plan is expired, renew your plan to access requests...')
            return redirect('user_profile')       
        elif 'limit' == parser.add_video_data(user_id=request.user.id):
            messages.warning(request, 'Your requests quota has exhausted, upgrade your plan to increase your limit...')
            return redirect('pricing')

        else:
            return redirect('pars')


def remove(request):
    profile = request.user.profile
    remove_list = [rem.name for rem in models.Remove.objects.filter(users_found_remove=profile)]
    for video in models.Video.objects.all():
        lst_websites = [i for i in video.websites_list]

        for link in lst_websites:
            for rem in remove_list:
                if rem in link:
                    video.websites_list.remove(link)

        video.save()

    return redirect('video_output')


def delete_quota(request):
    profile = request.user.profile
    profile.plan_start = None
    profile.plan_expired_on = None
    profile.quota = models.Quota.objects.get(name='default')
    profile.payment = False
    profile.plan_availiable_requests = 0
    profile.save()
    print('[INFO] Quota was successfully deleted, current user`s plan: "default"')

    messages.success(request, 'Quota was successfully deleted, current user`s plan: "default"')
    return redirect('user_profile')


def delete_photo(request):
    profile = request.user.profile
    profile.profile_photo = None
    profile.save()

    return redirect('user_profile')


def add_remove(request):
    website = request.GET.get('website')
    remove_list = models.Remove.objects.all()
    # profile = request.user.profile
    profile = request.user.profile

    if website and website not in remove_list:
        obj = models.Remove.objects.create(
            name=website,
        )
        created = True
        obj.users_found_remove.add(profile)

    return HttpResponse('Success')


def support(request):
    form = forms.FeedBackForm()
    if request.method == 'POST':
        form = forms.FeedBackForm(request.POST)
        writer = gmail_sender.GmailSender()

        if form.is_valid():
            if request.user.is_authenticated:
                user_email = request.user.email
            else:
                user_email = 'AnonimousUser'
            title = form.cleaned_data['title']
            category = form.cleaned_data['category']
            text = form.cleaned_data['text']

            writer.send_feedback_from_user(user_email=user_email, title=title, category=category,text=text)
            return redirect('support')

    return render(request, 'support.html', {'username': request.user.username, 'form': form})


@login_required
def add_deal(request):
    add_deal_form = forms.AddDealForm()
    document_form = forms.DocumentFormSet()
    if request.method == 'POST':
        profile = request.user.profile
        add_deal_form = forms.AddDealForm(request.POST)
        document_form = forms.DocumentFormSet(request.POST, request.FILES)
        print(request.FILES)
        print(add_deal_form.is_valid())
        print(document_form.is_valid())
        print(add_deal_form.is_valid() and document_form.is_valid())
        if add_deal_form.is_valid() and document_form.is_valid():
            defaults = {
                'brand': add_deal_form.cleaned_data.get('brand'),
                'status': add_deal_form.cleaned_data.get('status'),
                'date': add_deal_form.cleaned_data.get('date'),
                'email': add_deal_form.cleaned_data.get('email'),
                'phone_number': add_deal_form.cleaned_data.get('phone_number'),
                'rated_quoted': add_deal_form.cleaned_data.get('rated_quoted'),
                'counter_offer': add_deal_form.cleaned_data.get('counter_offer'),
                'agreed_rate': add_deal_form.cleaned_data.get('agreed_rate'),
                'introduction': add_deal_form.cleaned_data.get('introduction'),
                'pitch': add_deal_form.cleaned_data.get('pitch'),
                'views_impressions': add_deal_form.cleaned_data.get('views_impressions'),
                'views_amount': add_deal_form.cleaned_data.get('views_amount'),
                'affiliate_check': add_deal_form.cleaned_data.get('affiliate_check'),
                'affiliate_link': add_deal_form.cleaned_data.get('affiliate_link'),
                'commissions': add_deal_form.cleaned_data.get('commissions'),
                'comment': add_deal_form.cleaned_data.get('comment'),
            }
            obj = models.DealInfo.objects.create(
                name=add_deal_form.cleaned_data.get('name'),
                **defaults,
            )
            created = True  # Припускаємо, що об'єкт завжди створюється за допомогою create()
            obj.users_found_deal.add(profile)
            for form in document_form:
                print(form.cleaned_data.get('docfile'))
                if form.cleaned_data.get('docfile'):
                    docfile = form.cleaned_data.get('docfile')
                    file, created = models.Document.objects.get_or_create(docfile=docfile, title=docfile.name)
                    obj.document.add(file)
                    obj.save()

                    file_path = os.path.join(settings.MEDIA_ROOT, 'documents', docfile.name)
                    directory = os.path.dirname(file_path)
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    with open(file_path, 'wb') as destination:
                        for chunk in docfile.chunks():
                            destination.write(chunk)

            messages.success(request, message='Deal cuccessfully saved...')
            return redirect('deals')
        else:
            messages.warning(request, message=f'{document_form.errors}')  # TODO placeholder
            print(add_deal_form.errors)
            print(document_form.errors)

    context = {'add_deal_form': add_deal_form, "document_form": document_form}
    return render(request, 'deals/add-deal.html', context=context)


@login_required
def deal(request):
    profile = request.user.profile
    try:
        size = int(request.GET.get('size'))
        assert size > 0
    except:
        size = 15

    try:
        page_number = int(request.GET.get('page'))
        assert page_number > 0
    except:
        page_number = 1

    queryset = models.DealInfo.objects.filter(archive=False, users_found_deal=profile).order_by('-date')

    paginator = Paginator(queryset, size)

    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return redirect('deals')

    username = request.user.username
    count = models.Brand.objects.all().count()
    start = (page_number - 1)*size + 1
    end = page_number*size if count > page_number*size else count
    # context = {'deals': deals, 'page': page, 'size': size}
    return render(request, 'deals/deal.html', locals())


@login_required
def deals_in_archive(request):
    profile = request.user.profile
    try:
        size = int(request.GET.get('size'))
        assert size > 0
    except:
        size = 15

    try:
        page_number = int(request.GET.get('page'))
        assert page_number > 0
    except:
        page_number = 1

    queryset = models.DealInfo.objects.filter(archive=True, users_found_deal=profile).order_by('-date')

    paginator = Paginator(queryset, size)

    try:
        page = paginator.page(page_number)
    except EmptyPage:
        return redirect('deals_archive')

    username = request.user.username
    count = models.Brand.objects.all().count()
    start = (page_number - 1)*size + 1
    end = page_number*size if count > page_number*size else count
    # context = {'deals': deals, 'page': page, 'size': size}
    return render(request, 'deals/deal-archive.html', locals())


@login_required
def update_deal(request, obj_id):
    instance = get_object_or_404(models.DealInfo, id=obj_id)
    form = forms.AddDealForm(request.POST or None, instance=instance)
    print(form.is_valid())
    if form.is_valid():
        deal = form.save(commit=False)

        # Manually add the current user (profile) to the users_found_deal field
        profile = request.user.profile
        deal.users_found_deal.add(profile)

        # Now, save the instance to the database
        deal.save()
        return redirect('deals')
        # Отримання документів, пов'язаних з цим об'єктом DealInfo

    related_documents = instance.document.all()
    print(related_documents)

    return render(request, 'deals/add-deal.html', {'add_deal_form': form, 'related_documents': related_documents})



def delete_deal(request, obj_id):
    delete_obj = get_object_or_404(models.DealInfo, id=obj_id)
    delete_obj.delete()
    return redirect('deals')


def clone_deal(request, obj_id):
    original = get_object_or_404(models.DealInfo, id=obj_id)
    clone = models.DealInfo.objects.create(
        brand=original.brand,
        date=original.date,
        status=original.status,
        name=original.name,
        email=original.email,
        phone_number=original.phone_number,
        rated_quoted=original.rated_quoted,
        counter_offer=original.counter_offer,
        agreed_rate=original.agreed_rate,
        introduction=original.introduction,
        pitch=original.pitch,
        views_impressions=original.views_impressions,
        views_amount=original.views_amount,
        affiliate_check=original.affiliate_check,
        affiliate_link=original.affiliate_link,
        commissions=original.commissions,
        comment=original.comment,
    )
    # Копіюємо користувачів з оригінального поля до клонованого
    clone.users_found_deal.set(original.users_found_deal.all())

    # Копіюємо документи з оригінального поля до клонованого
    clone.document.set(original.document.all())
    return redirect('deals')


def archive_deal(request, obj_id):
    delete_obj = get_object_or_404(models.DealInfo, id=obj_id)
    delete_obj.archive = True
    delete_obj.save()
    return redirect('deals_archive')


def archived_archive_deal(request, obj_id):
    delete_obj = get_object_or_404(models.DealInfo, id=obj_id)
    delete_obj.archive = False
    delete_obj.save()
    return redirect('deals')


@login_required
def calendar(request):
    profile = request.user.profile
    deals = list(models.DealInfo.objects.filter(archive=False, users_found_deal=profile).values())
    return render(request, 'deals/calendar.html', {"deals": deals})


@login_required
def invoice(request):
    formset = forms.ItemFormSet()
    if request.method == 'POST':
        form = forms.InvoiceForm(request.POST, request.FILES)

        if form.is_valid():
            print('\n[INFO] invoice post request with valid form')
            items = []
            subtotal = 0

            for i in range(1000):
                description = request.POST.get(f'form-{i}-item_description')
                quantity = request.POST.get(f'form-{i}-quantity')
                rate = request.POST.get(f'form-{i}-rate')

                if any((description, quantity, rate)):
                    try:
                        amount = int(quantity) * int(rate)
                    except ValueError:
                        amount = 0
                    subtotal += amount
                    items.append((description, quantity, format(round(float(rate), 2), '.2f'), format(round(amount, 2), '.2f')))
                else: 
                    break

            print(request.POST)

            invoice_from = request.POST.get('invoice_from')

            print(invoice_from)
            bill_to = request.POST.get('bill_to')
            ship_to = request.POST.get('ship_to')
            invoice_tag = request.POST.get('invoice_tag')
            date, due_date = request.POST.getlist('date')[0], request.POST.getlist('date')[1]
            try:
                currency = request.POST.get('select-category').strip()[0]
            except IndexError:
                currency = '$'
            payment_terms = request.POST.get('payment_terms')
            po_number = request.POST.get('po_number')
            notes = request.POST.get('notes')
            terms = request.POST.get('terms')

            discount = form.cleaned_data.get('discount')
            if request.POST.get('discount%') == 'true':
                discount = subtotal * discount / 100

            tax = form.cleaned_data.get('tax')
            if request.POST.get('tax%') == 'true':
                tax = subtotal * tax / 100

            shipping = form.cleaned_data.get('shipping')
            amount_paid = form.cleaned_data.get('amount_paid')

            total = subtotal - discount + tax + shipping
            balance_due = total - amount_paid

            logo = form.cleaned_data.get('logo')
            saved_logo_path = None
            if logo:
                saved_logo_path = os.path.join(settings.MEDIA_ROOT, logo.name)
                with open(saved_logo_path, 'wb') as f:
                    for chunk in logo.chunks():
                        f.write(chunk)
            context = {
                "invoice_from": invoice_from,
                "bill_to": bill_to,
                "ship_to": ship_to,
                "invoice_tag": invoice_tag,
                "date": date,
                "due_date": due_date,
                "payment_terms": payment_terms,
                "po_number": po_number,
                "items": items,
                "discount": format(round(discount, 2), '.2f'),
                "tax": tax,
                "shipping": shipping,
                "amount_paid": format(round(amount_paid, 2), '.2f'),
                "subtotal": format(round(subtotal, 2), '.2f'),
                "total": format(round(total, 2), '.2f'),
                "balance_due": format(round(balance_due, 2), '.2f'),
                "notes": notes,
                "terms": terms,
                'currency': currency, 
                "image": None, 
            }

            if saved_logo_path:
                context['image'] = saved_logo_path
            # return render(request, "invoice-data.html", context)
            render_html = render(request, "invoice-data.html", context).content.decode('utf-8')
            config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                pdfkit.from_string(
                    render_html,
                    output_path=temp_file.name,
                    configuration=config,
                    options={"enable-local-file-access": ""},
                )
                temp_file.close()

                with open(temp_file.name, 'rb') as pdf_file:
                    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
                    return response

        else:
            print(form.errors)
            print(formset.errors)

    return render(request, 'invoice.html', {'form': forms.InvoiceForm, 'formsets': formset})


def invoice_data_view(request):
    return render(request, 'invoice-data.html')


########################################################################################################
# PAYMENTS # 

def payment_redirect_view(request):
    if request.method == 'POST':
        paysystem = request.POST.get('paysystem')
        subscription = request.POST.get('subscription')

        if paysystem == 'Stripe':
            return redirect(f'stripe_create_checkout_session/?plan={subscription}', permanent=True)
        elif paysystem == 'PayPal':
            return redirect(f'paypal_create_checkout_session/?plan={subscription}', permanent=True)

    return JsonResponse({'type': 'payment_session manager'})


#################################################################################################
# STRIPE PAYMENT #

def stripe_create_checkout_session_view(request):

    stripe.api_key = settings.STRIPE_API_KEY

    domain = settings.CURRENT_HOST
    temp_token = secrets.token_urlsafe(64)
    profile = request.user.profile
    plan = request.GET.get('plan')

    plans_prices = {
        'Low': 'price_1NXPL9IMpcyvQQ9E1tyVHfdD', 
        'Medium': 'price_1NXPKwIMpcyvQQ9EE9z7wnCu', 
        'Pro': 'price_1NXPG3IMpcyvQQ9EC8IvwEkL', 
    }
    # try:
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                'price': plans_prices.get(plan), 
                'quantity': 1,
            },
        ],
        mode='subscription',
        success_url= f'{domain}/success_payment/{plan}/{temp_token}',
        cancel_url= f'{domain}/pracing/',
    )
    profile.temp_token = temp_token
    profile.save()
    return redirect(checkout_session.url, code=303)
    # except Exception as ex:
    #     print(ex)


########################################################################################################
# PAYPAL PAYMENT #

def paypal_create_checkout_session_view(request):

    domain = settings.CURRENT_HOST
    temp_token = secrets.token_urlsafe(64)
    profile = request.user.profile
    plan = request.GET.get('plan')  

    set_config(
        client_id=settings.PAYPAL_CLIENT_ID, 
        client_secret=settings.PAYPAL_CLIENT_SECRET
    )
    plans_prices = {
        'Low': {'price':'39.00', 'description': 'Low subscription payment'}, 
        'Medium': {'price':'99.00', 'description': 'Medium subscription payment'}, 
        'Pro': {'price':'249.00', 'description': 'Pro subscription payment'}, 
    }
    # try:
    paypal_payment = Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": f'{domain}/success_payment/{plan}/{temp_token}/',
            "cancel_url": f'{domain}/pracing/'
        },
        "transactions": [{
            "amount": {
                "total": plans_prices.get(plan).get('price'),  # Replace with your payment amount
                "currency": "USD"  # Replace with your preferred currency
            },
            "description": plans_prices.get(plan).get('description')
        }]
    })
    profile.temp_token = temp_token
    profile.save()
    if paypal_payment.create():
        return redirect(paypal_payment['links'][1]['href'], code=303)
    else:
        return JsonResponse({"error": paypal_payment.error})
    # except Exception as ex:
    #     print(ex)


def success_payment_view(request, plan, temp_token):
    # collect paypal additional data
    payment_id = request.GET.get('paymentId')
    token = request.GET.get('token')
    payer_id = request.GET.get('PayerID')


    try:
        profile = models.Profile.objects.get(temp_token=temp_token)
        quota = models.Quota.objects.get(name=plan)
        profile.quota = quota
        profile.plan_start = timezone.now()
        profile.plan_expired_on = timezone.now() + timedelta(days=30)
        profile.plan_availiable_requests += quota.requests
        profile.plan_expired = False
        profile.payment = True
        profile.temp_token = None
        profile.save()
        messages.success(request, 'Your plan was purchased successfully...')
    except ObjectDoesNotExist:
        messages.error(request, 'Payment failed.')

    return redirect('user_profile')


########################################################################################################
# SALES #

@login_required
def drug_and_door(request):
    profile = request.user.profile
    drug_and_door_cols = models.DrugAndDoorCol.objects.filter(users_found_pipeline=profile)
    context = {
        'drug_and_door_cols': drug_and_door_cols,
    }
    return render(request, 'drug_and_door.html', context)


@csrf_exempt
def update_column_positions(request):
    if request.method == "POST":
        profile = request.user.profile
        column_order = request.POST.get("order")
        if column_order:
            column_order = column_order.split(",")

            # Оновлення позицій у базі даних
            for position, col_id in enumerate(column_order, 1):
                try:
                    col = models.DrugAndDoorCol.objects.get(id=col_id, users_found_pipeline=profile)
                    col.position = position
                    col.save()
                except models.DrugAndDoorCol.DoesNotExist:
                    pass

            return JsonResponse({"message": "Позиції оновлено успішно!"})

    return JsonResponse({"error": "Помилка при оновленні позицій."}, status=400)


@csrf_exempt
def delete_column(request):
    if request.method == "POST":
        profile = request.user.profile
        col_id = request.POST.get("col_id")
        if col_id:
            try:
                col = models.DrugAndDoorCol.objects.get(id=col_id, users_found_pipeline=profile)
                col.delete()

                # Оновлюємо позиції у базі даних після видалення
                cols = models.DrugAndDoorCol.objects.filter(users_found_pipeline=profile).order_by('position')
                for position, col in enumerate(cols, 1):
                    col.position = position
                    col.save()

                return JsonResponse({"message": "Колонка видалена успішно!"})
            except models.DrugAndDoorCol.DoesNotExist:
                pass

    return JsonResponse({"error": "Помилка при видаленні колонки."}, status=400)


@csrf_exempt
def move_field(request):
    if request.method == "POST":
        col_id = request.POST.get("col_id")
        field_id = request.POST.get("field_id")
        profile = request.user.profile

        if col_id and field_id:
            try:
                col = models.DrugAndDoorCol.objects.get(id=col_id, users_found_pipeline=profile)
                field = models.DrugAndDoorField.objects.get(id=field_id, users_found_pipeline=profile)
                new_position = int(request.POST.get("new_position"))

                print(field.position)

                # Зберігаємо стару колонку для оновлення позицій
                old_col = field.drug_and_door_col

                # Отримуємо всі поля у новій колонці, впорядковані за позиціями
                fields_in_new_col = models.DrugAndDoorField.objects.filter(drug_and_door_col=col, users_found_pipeline=profile).order_by('position')

                print(new_position, 'new_position')

                if field in fields_in_new_col:
                    # Видаляємо поточне поле зі списку
                    fields_in_new_col = [f for f in fields_in_new_col if f != field]

                # Оновлюємо позиції полів у новій колонці
                for position, field_in_new_col in enumerate(fields_in_new_col, 1):

                    if position == new_position:
                        field_in_new_col.position = position + 1
                        field_in_new_col.save()
                    elif position > new_position:
                        field_in_new_col.position = position + 1
                        field_in_new_col.save()
                    else:
                        field_in_new_col.position = position
                        field_in_new_col.save()

                field.drug_and_door_col = col
                field.position = new_position

                field.save()

                # Оновлюємо позиції у старій колонці
                fields_in_old_col = models.DrugAndDoorField.objects.filter(drug_and_door_col=old_col, users_found_pipeline=profile).order_by('position')
                for position, field_in_old_col in enumerate(fields_in_old_col, 1):
                    field_in_old_col.position = position
                    field_in_old_col.save()  # Зберігаємо зміни у базі даних

                return JsonResponse({"message": "Поле переміщено успішно!"})
            except (models.DrugAndDoorCol.DoesNotExist, models.DrugAndDoorField.DoesNotExist):
                pass

    return JsonResponse({"error": "Помилка при переміщенні поля."}, status=400)


# Функція для видалення поля
@csrf_exempt
def delete_field(request):
    if request.method == "POST":
        field_id = request.POST.get("field_id")
        profile = request.user.profile

        if field_id:
            try:
                field = models.DrugAndDoorField.objects.get(id=field_id, users_found_pipeline=profile)

                # Зберігаємо стару колонку для оновлення позицій
                col = field.drug_and_door_col

                # Видаляємо поле
                field.delete()

                # Оновлюємо позиції полів у колонці
                fields_in_col = models.DrugAndDoorField.objects.filter(drug_and_door_col=col, users_found_pipeline=profile).order_by('position')
                for position, field_in_col in enumerate(fields_in_col, 1):
                    field_in_col.position = position
                    field_in_col.save()

                return JsonResponse({"message": "Поле видалено успішно!"})
            except models.DrugAndDoorField.DoesNotExist:
                pass

    return JsonResponse({"error": "Помилка при видаленні поля."}, status=400)


@csrf_exempt
def add_field(request):
    if request.method == "POST":
        col_id = request.POST.get("col_id")
        name = request.POST.get("name")
        price = request.POST.get("price")
        profile = request.user.profile

        if col_id and name and price:
            try:
                col = models.DrugAndDoorCol.objects.get(id=col_id, users_found_pipeline=profile)

                # Отримуємо кількість полів у колонці
                num_fields_in_col = models.DrugAndDoorField.objects.filter(drug_and_door_col=col, users_found_pipeline=profile).count()

                # Створюємо нове поле та зберігаємо його
                # field = models.DrugAndDoorField(name=name, price=price, drug_and_door_col=col, position=num_fields_in_col + 1)
                # field.save()
                obj = models.DrugAndDoorField.objects.create(
                    name=name,
                    price=price,
                    drug_and_door_col=col,
                    position=num_fields_in_col + 1,
                )
                created = True  # Припускаємо, що об'єкт завжди створюється за допомогою create()
                obj.users_found_pipeline.add(profile)

                return JsonResponse({"message": "Поле додано успішно!"})
            except models.DrugAndDoorCol.DoesNotExist:
                pass

    return JsonResponse({"error": "Помилка при додаванні поля."}, status=400)


@csrf_exempt
def add_column(request):
    if request.method == "POST":
        profile = request.user.profile
        name = request.POST.get("name")

        if name:
            # Знаходимо кількість існуючих колонок

            existing_columns_count = models.DrugAndDoorCol.objects.filter(users_found_pipeline=profile).count()

            # Створюємо нову колонку та присвоюємо їй позицію
            # col = models.DrugAndDoorCol(name=name, position=existing_columns_count + 1)
            # col.save()
            # profile.users_found_pipeline.add(col)

            obj = models.DrugAndDoorCol.objects.create(
                name=name,
                position=existing_columns_count + 1,
            )
            created = True  # Припускаємо, що об'єкт завжди створюється за допомогою create()
            obj.users_found_pipeline.add(profile)

            return JsonResponse({"message": "Колонку додано успішно!"})
        else:
            return JsonResponse({"error": "Не вдалося додати колонку. Назва не може бути порожньою."}, status=400)

    return JsonResponse({"error": "Помилка при додаванні колонки."}, status=400)


@csrf_exempt
def update_stars(request):
    if request.method == 'POST':
        field_id = request.POST.get('field_id')
        stars = request.POST.get('stars')

        try:
            # Знаходимо об'єкт models.DrugAndDoorField за допомогою ID
            field = models.DrugAndDoorField.objects.get(id=field_id)

            # Перевіряємо, чи введене значення 'stars' є допустимим
            stars = int(stars)
            if stars not in [0, 1, 2, 3]:
                return JsonResponse({'error': 'Недопустиме значення зірочки!'}, status=400)

            # Оновлюємо значення поля 'stars'
            field.stars = stars
            field.save()

            # Після оновлення значення, повертаємо відповідь у форматі JSON
            return JsonResponse({'message': 'Значення stars оновлено успішно!'})
        except models.DrugAndDoorField.DoesNotExist:
            return JsonResponse({'error': 'Поле не знайдено!'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Недопустиме значення зірочки!'}, status=400)
    else:
        # Якщо метод запиту не є POST, повертаємо помилку
        return JsonResponse({'error': 'Метод запиту не підтримується!'}, status=400)
