import secrets as _secrets
import urllib.parse as _urlparse
import requests as _requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.conf import settings as django_settings
from django.utils import timezone
from datetime import date

from .models import KeyType, Key, KeyAssignment, Person


# ── Auth-Hilfsfunktion ────────────────────────────────────────────────────────

def _require_verwalter(request):
    """Gibt None zurück wenn Zugriff OK, sonst einen Redirect."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect(f'/auth/login/?next={request.path}')
    return None


# ── Dashboard ─────────────────────────────────────────────────────────────────

def dashboard(request):
    guard = _require_verwalter(request)
    if guard:
        return guard

    # Lade alle Typen mit Schlüsseln und deren aktuellen Vergaben in einem Query
    key_types = KeyType.objects.prefetch_related(
        'keys__assignments__person'
    ).all()

    # Statistik + Schlüssel-Details pro Typ
    type_sections = []
    for kt in key_types:
        keys = list(kt.keys.all())
        total    = len(keys)
        assigned = sum(1 for k in keys if k.is_assigned())
        type_sections.append({
            'type': kt,
            'keys': keys,
            'total': total,
            'assigned': assigned,
            'available': total - assigned,
        })

    return render(request, 'keys/dashboard.html', {
        'type_sections': type_sections,
        'key_types': key_types,
    })


def key_list(request, type_id=None):
    """Alle Schlüssel eines Typs mit aktuellem Status."""
    guard = _require_verwalter(request)
    if guard:
        return guard

    key_types = KeyType.objects.all()
    selected_type = None
    keys = Key.objects.select_related('key_type').prefetch_related('assignments')

    if type_id:
        selected_type = get_object_or_404(KeyType, pk=type_id)
        keys = keys.filter(key_type=selected_type)

    return render(request, 'keys/key_list.html', {
        'keys': keys,
        'key_types': key_types,
        'selected_type': selected_type,
    })


def assign_key(request, key_id):
    """Schlüssel an eine Person ausgeben."""
    guard = _require_verwalter(request)
    if guard:
        return guard

    key = get_object_or_404(Key, pk=key_id)

    if key.is_assigned():
        messages.error(request, f'Schlüssel "{key}" ist bereits vergeben.')
        return redirect('dashboard')

    if request.method == 'POST':
        person_id   = request.POST.get('person_id', '').strip()
        issued_date = request.POST.get('issued_date', '')
        notes       = request.POST.get('notes', '').strip()

        person = Person.objects.filter(pk=person_id).first() if person_id else None

        if not person or not issued_date:
            messages.error(request, 'Bitte eine Person auswählen und das Ausgabedatum angeben.')
        else:
            KeyAssignment.objects.create(
                key=key,
                person=person,
                issued_date=issued_date,
                issued_by=request.user.get_full_name() or request.user.username,
                notes=notes,
            )
            messages.success(request, f'Schlüssel "{key}" wurde an {person.name} ausgegeben.')
            return redirect('dashboard')

    persons = Person.objects.filter(is_active=True)
    return render(request, 'keys/assign.html', {
        'key': key,
        'today': date.today().isoformat(),
        'persons': persons,
    })


def return_key(request, assignment_id):
    """Schlüssel als zurückgegeben markieren."""
    guard = _require_verwalter(request)
    if guard:
        return guard

    assignment = get_object_or_404(KeyAssignment, pk=assignment_id, return_date__isnull=True)

    if request.method == 'POST':
        return_date = request.POST.get('return_date', '')
        if not return_date:
            messages.error(request, 'Bitte Rückgabedatum angeben.')
        else:
            assignment.return_date = return_date
            assignment.save(update_fields=['return_date'])
            messages.success(
                request,
                f'Schlüssel "{assignment.key}" von {assignment.person.name} als zurückgegeben markiert.'
            )
            return redirect('dashboard')

    return render(request, 'keys/return_key.html', {
        'assignment': assignment,
        'today': date.today().isoformat(),
    })


def history(request):
    """Vollständige Vergabe-Historie."""
    guard = _require_verwalter(request)
    if guard:
        return guard

    assignments = KeyAssignment.objects.select_related('key__key_type', 'person').order_by('-issued_date', '-created')

    filter_name = request.GET.get('name', '').strip()
    filter_type = request.GET.get('type', '')
    filter_open = request.GET.get('open', '')

    if filter_name:
        assignments = assignments.filter(person__name__icontains=filter_name)
    if filter_type:
        assignments = assignments.filter(key__key_type_id=filter_type)
    if filter_open == '1':
        assignments = assignments.filter(return_date__isnull=True)

    key_types = KeyType.objects.all()
    return render(request, 'keys/history.html', {
        'assignments': assignments,
        'key_types': key_types,
        'filter_name': filter_name,
        'filter_type': filter_type,
        'filter_open': filter_open,
    })


# ── OIDC Auth ─────────────────────────────────────────────────────────────────

# ── Verwaltung: Schlüsseltypen & Schlüssel ───────────────────────────────────

def manage(request):
    """Stammdaten-Verwaltung: Schlüsseltypen und Schlüssel anlegen/bearbeiten/löschen."""
    guard = _require_verwalter(request)
    if guard:
        return guard

    key_types = KeyType.objects.prefetch_related('keys').all()
    persons   = Person.objects.all()
    return render(request, 'keys/manage.html', {'key_types': key_types, 'persons': persons})


def keytype_create(request):
    guard = _require_verwalter(request)
    if guard:
        return guard
    if request.method == 'POST':
        name  = request.POST.get('name', '').strip()
        desc  = request.POST.get('description', '').strip()
        color = request.POST.get('color', '#c0000c').strip()
        order = request.POST.get('order', '0').strip()
        if name:
            KeyType.objects.create(name=name, description=desc, color=color or '#c0000c',
                                   order=int(order) if order.isdigit() else 0)
            messages.success(request, f'Schlüsseltyp „{name}" angelegt.')
        else:
            messages.error(request, 'Bezeichnung ist ein Pflichtfeld.')
    return redirect('manage')


def keytype_edit(request, type_id):
    guard = _require_verwalter(request)
    if guard:
        return guard
    kt = get_object_or_404(KeyType, pk=type_id)
    if request.method == 'POST':
        name  = request.POST.get('name', '').strip()
        desc  = request.POST.get('description', '').strip()
        color = request.POST.get('color', '#c0000c').strip()
        order = request.POST.get('order', '0').strip()
        if name:
            kt.name        = name
            kt.description = desc
            kt.color       = color or '#c0000c'
            kt.order       = int(order) if order.isdigit() else 0
            kt.save()
            messages.success(request, f'Schlüsseltyp „{name}" aktualisiert.')
            return redirect('manage')
        else:
            messages.error(request, 'Bezeichnung ist ein Pflichtfeld.')
    return render(request, 'keys/keytype_form.html', {'kt': kt})


def keytype_delete(request, type_id):
    guard = _require_verwalter(request)
    if guard:
        return guard
    kt = get_object_or_404(KeyType, pk=type_id)
    if request.method == 'POST':
        if kt.keys.exists():
            messages.error(request, f'Schlüsseltyp „{kt.name}" kann nicht gelöscht werden, da noch Schlüssel zugeordnet sind.')
        else:
            kt.delete()
            messages.success(request, f'Schlüsseltyp gelöscht.')
    return redirect('manage')


def key_create(request):
    guard = _require_verwalter(request)
    if guard:
        return guard
    if request.method == 'POST':
        type_id = request.POST.get('key_type', '')
        number  = request.POST.get('number', '').strip()
        notes   = request.POST.get('notes', '').strip()
        if type_id and number:
            kt = get_object_or_404(KeyType, pk=type_id)
            Key.objects.create(key_type=kt, number=number, notes=notes)
            messages.success(request, f'Schlüssel „{number}" angelegt.')
        else:
            messages.error(request, 'Typ und Bezeichnung sind Pflichtfelder.')
    return redirect('manage')


def key_edit(request, key_id):
    guard = _require_verwalter(request)
    if guard:
        return guard
    key = get_object_or_404(Key, pk=key_id)
    if request.method == 'POST':
        type_id = request.POST.get('key_type', '')
        number  = request.POST.get('number', '').strip()
        notes   = request.POST.get('notes', '').strip()
        if type_id and number:
            key.key_type = get_object_or_404(KeyType, pk=type_id)
            key.number   = number
            key.notes    = notes
            key.save()
            messages.success(request, f'Schlüssel „{number}" aktualisiert.')
            return redirect('manage')
        else:
            messages.error(request, 'Typ und Bezeichnung sind Pflichtfelder.')
    key_types = KeyType.objects.all()
    return render(request, 'keys/key_form.html', {'key': key, 'key_types': key_types})


def key_delete(request, key_id):
    guard = _require_verwalter(request)
    if guard:
        return guard
    key = get_object_or_404(Key, pk=key_id)
    if request.method == 'POST':
        if key.is_assigned():
            messages.error(request, f'Schlüssel „{key}" ist aktuell vergeben und kann nicht gelöscht werden.')
        else:
            label = str(key)
            key.delete()
            messages.success(request, f'Schlüssel „{label}" gelöscht.')
    return redirect('manage')


# ── Personen-Verwaltung ───────────────────────────────────────────────────────

def person_create(request):
    guard = _require_verwalter(request)
    if guard:
        return guard
    if request.method == 'POST':
        name  = request.POST.get('name', '').strip()
        role  = request.POST.get('role', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        notes = request.POST.get('notes', '').strip()
        if name:
            Person.objects.create(name=name, role=role, email=email, phone=phone, notes=notes)
            messages.success(request, f'Person „{name}" angelegt.')
        else:
            messages.error(request, 'Name ist ein Pflichtfeld.')
    return redirect('manage')


def person_edit(request, person_id):
    guard = _require_verwalter(request)
    if guard:
        return guard
    person = get_object_or_404(Person, pk=person_id)
    if request.method == 'POST':
        name  = request.POST.get('name', '').strip()
        role  = request.POST.get('role', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        notes = request.POST.get('notes', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        if name:
            person.name      = name
            person.role      = role
            person.email     = email
            person.phone     = phone
            person.notes     = notes
            person.is_active = is_active
            person.save()
            messages.success(request, f'Person „{name}" aktualisiert.')
            return redirect('manage')
        else:
            messages.error(request, 'Name ist ein Pflichtfeld.')
    return render(request, 'keys/person_form.html', {'person': person})


def person_delete(request, person_id):
    guard = _require_verwalter(request)
    if guard:
        return guard
    person = get_object_or_404(Person, pk=person_id)
    if request.method == 'POST':
        if person.assignments.exists():
            messages.error(request, f'Person „{person.name}" kann nicht gelöscht werden – es existieren Schlüsselvergaben (aktiv oder historisch).')
        else:
            name = person.name
            person.delete()
            messages.success(request, f'Person „{name}" gelöscht.')
    return redirect('manage')


# ── OIDC Auth ─────────────────────────────────────────────────────────────────

def oidc_login(request):
    base_url   = getattr(django_settings, 'OIDC_BASE_URL', '').rstrip('/')
    client_id  = getattr(django_settings, 'OIDC_CLIENT_ID', '')
    redirect_uri = getattr(django_settings, 'OIDC_REDIRECT_URI', '')

    if not base_url or not client_id:
        messages.error(request, 'OIDC nicht konfiguriert.')
        return redirect('dashboard')

    state = _secrets.token_urlsafe(32)
    request.session['oidc_state'] = state

    next_url = request.GET.get('next', '/')
    parsed = _urlparse.urlparse(next_url)
    if parsed.scheme or parsed.netloc:
        next_url = '/'
    request.session['oidc_next'] = next_url

    params = _urlparse.urlencode({
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'openid email profile roles',
        'state': state,
    })
    return redirect(f'{base_url}/o/authorize/?{params}')


def oidc_callback(request):
    from django.contrib.auth.models import User

    state = request.GET.get('state')
    if not state or state != request.session.pop('oidc_state', None):
        messages.error(request, 'Anmeldung fehlgeschlagen – bitte erneut versuchen.')
        return redirect('dashboard')

    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Kein Authentifizierungscode erhalten.')
        return redirect('dashboard')

    internal_url = getattr(django_settings, 'OIDC_INTERNAL_URL',
                           getattr(django_settings, 'OIDC_BASE_URL', '')).rstrip('/')
    try:
        token_resp = _requests.post(
            f'{internal_url}/o/token/',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': getattr(django_settings, 'OIDC_REDIRECT_URI', ''),
                'client_id': getattr(django_settings, 'OIDC_CLIENT_ID', ''),
                'client_secret': getattr(django_settings, 'OIDC_CLIENT_SECRET', ''),
            },
            timeout=10,
        )
        token_resp.raise_for_status()
        access_token = token_resp.json().get('access_token', '')

        userinfo_resp = _requests.get(
            f'{internal_url}/o/userinfo/',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
        userinfo_resp.raise_for_status()
        userinfo = userinfo_resp.json()
    except (_requests.RequestException, ValueError):
        messages.error(request, 'Fehler bei der Verbindung zum Authentifizierungsserver.')
        return redirect('dashboard')

    email = userinfo.get('email', '').lower().strip()
    name  = userinfo.get('name', '')
    roles = userinfo.get('roles', {})
    sv_role = roles.get('schluesselverwaltung', {}).get('role', '')

    # 'verwaltung'-Rolle aus ClubAuth = Verwalter-Zugriff
    # 'admin'-Rolle = Superuser
    if not email or sv_role not in ('verwaltung', 'admin'):
        messages.error(request, 'Kein Zugriff auf die Schlüsselverwaltung.')
        return redirect('dashboard')

    parts = name.split(' ', 1)
    first_name = parts[0] if parts else ''
    last_name  = parts[1] if len(parts) > 1 else ''

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        users_by_email = User.objects.filter(email__iexact=email)
        if users_by_email.exists():
            user = users_by_email.filter(username=email).first() \
                   or users_by_email.order_by('date_joined').first()
        else:
            user = User.objects.create_user(
                username=email, email=email,
                first_name=first_name, last_name=last_name,
            )

    user.is_staff     = True
    user.is_active    = True
    user.is_superuser = (sv_role == 'admin')
    if first_name: user.first_name = first_name
    if last_name:  user.last_name  = last_name
    user.save(update_fields=['is_staff', 'is_active', 'is_superuser', 'first_name', 'last_name'])

    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    next_url = request.session.pop('oidc_next', '/')
    return redirect(next_url)


def oidc_logout(request):
    auth_logout(request)
    base_url = getattr(django_settings, 'OIDC_BASE_URL', '').rstrip('/')
    return redirect(f'{base_url}/accounts/logout/')
