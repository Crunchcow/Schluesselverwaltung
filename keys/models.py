from django.db import models


class KeyType(models.Model):
    """Schlüsseltyp: z.B. Generalschlüssel, Vereinsheim, Stadion"""
    name = models.CharField(max_length=100, verbose_name='Bezeichnung')
    description = models.TextField(blank=True, verbose_name='Beschreibung')
    color = models.CharField(
        max_length=7, default='#c0000c',
        verbose_name='Farbe (Hex)',
        help_text='Farbe zur visuellen Unterscheidung, z.B. #c0000c',
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Reihenfolge')

    class Meta:
        verbose_name = 'Schlüsseltyp'
        verbose_name_plural = 'Schlüsseltypen'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def assigned_count(self):
        return sum(1 for k in self.keys.all() if k.is_assigned())

    def available_count(self):
        return self.keys.count() - self.assigned_count()


class Key(models.Model):
    """Einzelner physischer Schlüssel"""
    key_type = models.ForeignKey(
        KeyType, on_delete=models.CASCADE,
        related_name='keys', verbose_name='Schlüsseltyp',
    )
    number = models.CharField(max_length=50, verbose_name='Schlüsselnummer / Bezeichnung',
                              help_text='z.B. "Nr. 1" oder "Schlüssel A"')
    notes = models.TextField(blank=True, verbose_name='Bemerkungen')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Schlüssel'
        verbose_name_plural = 'Schlüssel'
        ordering = ['key_type__order', 'key_type__name', 'number']

    def __str__(self):
        return f'{self.key_type.name} – {self.number}'

    def is_assigned(self):
        return self.assignments.filter(return_date__isnull=True).exists()

    def current_assignment(self):
        return self.assignments.filter(return_date__isnull=True).first()


class Person(models.Model):
    """Bekannte Schlüsselempfänger (Reinigungskräfte, Hausmeister, …)"""
    name = models.CharField(max_length=200, verbose_name='Name')
    role = models.CharField(max_length=100, blank=True, verbose_name='Funktion',
                            help_text='z.B. Hausmeister, Reinigungskraft, Trainer')
    email = models.EmailField(blank=True, verbose_name='E-Mail')
    phone = models.CharField(max_length=50, blank=True, verbose_name='Telefon')
    notes = models.TextField(blank=True, verbose_name='Bemerkungen')
    is_active = models.BooleanField(default=True, verbose_name='Aktiv')

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'Personen'
        ordering = ['name']

    def __str__(self):
        if self.role:
            return f'{self.name} ({self.role})'
        return self.name


class KeyAssignment(models.Model):
    """Ausgabe und Rücknahme eines Schlüssels"""
    key = models.ForeignKey(
        Key, on_delete=models.CASCADE,
        related_name='assignments', verbose_name='Schlüssel',
    )
    person = models.ForeignKey(
        Person, on_delete=models.PROTECT,
        related_name='assignments', verbose_name='Person',
    )
    issued_date = models.DateField(verbose_name='Ausgabedatum')
    return_date = models.DateField(null=True, blank=True, verbose_name='Rückgabedatum')
    issued_by = models.CharField(max_length=200, blank=True, verbose_name='Ausgegeben von')
    notes = models.TextField(blank=True, verbose_name='Bemerkungen')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Schlüsselvergabe'
        verbose_name_plural = 'Schlüsselvergaben'
        ordering = ['-issued_date', '-created']

    def __str__(self):
        status = 'ausgegeben' if not self.return_date else f'zurück am {self.return_date}'
        return f'{self.key} → {self.holder_name} ({status})'

    @property
    def is_active(self):
        return self.return_date is None
