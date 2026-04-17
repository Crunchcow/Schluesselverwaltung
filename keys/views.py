import secrets as _secrets
import urllib.parse as _urlparse
import requests as _requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.conf import settings as django_settings
from django.utils import timezone
from datetime import date

from .models import KeyType, Key, KeyAssignment


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

    key_types = KeyType.objects.prefetch_related('keys__assignments').all()

    # Filter aus GET
    filter_status = request.GET.get('status', '')  # 'assigned' | 'available' | ''
    filter_type   = request.GET.get('type', '')

    # Alle aktiven Vergaben (für Gesamtübersicht)
    active_assignments = KeyAssignment.objects.filter(
        return_date__isnull=True
    ).select_related('key__key_type').order_by('holder_name')

    if filter_status == 'assigned':
        active_assignments = active_assignments
    elif filter_status == 'available':
        active_assignments = KeyAssignment.objects.none()

    if filter_type:
        active_assignments = active_assignments.filter(key__key_type_id=filter_type)

    # Statistik pro Typ
    type_stats = []
    for kt in key_types:
        keys = list(kt.keys.all())
        total    = len(keys)
        assigned = sum(1 for k in keys if k.is_assigned())
        type_stats.append({
            'type': kt,
            'total': total,
            'assigned': assigned,
            'available': total - assigned,
        })

    return render(request, 'keys/dashboard.html', {
        'type_stats': type_stats,
        'active_assignments': active_assignments,
        'filter_status': filter_status,
        'filter_type': filter_type,
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
        holder_name  = request.POST.get('holder_name', '').strip()
        holder_email = request.POST.get('holder_email', '').strip()
        holder_phone = request.POST.get('holder_phone', '').strip()
        issued_date  = request.POST.get('issued_date', '')
        notes        = request.POST.get('notes', '').strip()

        if not holder_name or not issued_date:
            messages.error(request, 'Name und Ausgabedatum sind Pflichtfelder.')
        else:
            KeyAssignment.objects.create(
                key=key,
                holder_name=holder_name,
                holder_email=holder_email,
                holder_phone=holder_phone,
                issued_date=issued_date,
                issued_by=request.user.get_full_name() or request.user.username,
                notes=notes,
            )
            messages.success(request, f'Schlüssel "{key}" wurde an {holder_name} ausgegeben.')
            return redirect('dashboard')

    return render(request, 'keys/assign.html', {
        'key': key,
        'today': date.today().isoformat(),
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
                f'Schlüssel "{assignment.key}" von {assignment.holder_name} als zurückgegeben markiert.'
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

    assignments = KeyAssignment.objects.select_related('key__key_type').order_by('-issued_date', '-created')

    filter_name = request.GET.get('name', '').strip()
    filter_type = request.GET.get('type', '')
    filter_open = request.GET.get('open', '')

    if filter_name:
        assignments = assignments.filter(holder_name__icontains=filter_name)
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
