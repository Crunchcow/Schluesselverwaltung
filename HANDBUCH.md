# Schlüsselverwaltung - Benutzerhandbuch

## Projektübersicht

Die **Schlüsselverwaltung** ist eine webbasierte Anwendung zur Verwaltung aller Vereinsschlüssel. Sie ermöglicht die lückenlose Nachverfolgung von Schlüsselausgaben und -rückgaben an berechtigte Personen.

---

## Für Administratoren und Schlüsselverwalter

### Admin-Zugang
- **URL:** `https://[domain]/admin/`
- **Login:** Mit Ihren Admin-Zugangsdaten

### Hauptfunktionen im Admin-Bereich

#### 1. Schlüsseltypen verwalten
Unter **Schlüsseltypen** können Sie:
- Neue Schlüsselarten anlegen (z.B. Generalschlüssel, Vereinsheim, Stadion)
- Beschreibungen und Farben zur visuellen Unterscheidung festlegen
- Gesamtanzahl der vorhandenen Schlüssel pro Typ definieren
- Reihenfolge für die Anordnung festlegen

**Beispiele für Schlüsseltypen:**
- Generalschlüssel (rot)
- Vereinsheim (blau)
- Umkleidekabinen (grün)
- Geräteraum (gelb)
- Sportplatz (orange)

#### 2. Personen verwalten
Unter **Personen** können Sie:
- Berechtigte Schlüsselempfänger anlegen
- Kontaktdaten und Funktionen verwalten
- Aktivitätsstatus pflegen

**Typische Personen:**
- Hausmeister
- Reinigungskräfte
- Trainer
- Abteilungsleiter
- Verwaltungspersonal

#### 3. Schlüsselvergaben verwalten
Unter **Schlüsselvergaben** können Sie:
- Ausgaben und Rückgaben dokumentieren
- Aktuelle Vergaben einsehen
- Historie aller Zuweisungen anzeigen
- Überfällige Rückgaben identifizieren

---

## Für Schlüsselverwalter (tägliche Nutzung)

### Schlüssel ausgeben

#### 1. Person auswählen
1. Admin-Bereich → Personen
2. Empfänger auswählen oder neu anlegen
3. Kontaktdaten prüfen

#### 2. Schlüsselvergabe anlegen
1. Admin-Bereich → Schlüsselvergaben → Add
2. **Schlüsseltyp** auswählen
3. **Person** zuweisen
4. **Schlüsselnummer** eintragen (falls bekannt/graviert)
5. **Ausgabedatum** setzen (Standard: heute)
6. **Ausgegeben von** eintragen (Ihr Name)
7. **Bemerkungen** hinzufügen (falls erforderlich)
8. Speichern

#### 3. Verfügbarkeit prüfen
- Bei jedem Schlüsseltyp wird die Verfügbarkeit angezeigt
- **Gesamtanzahl:** Vorhandene Schlüssel
- **Vergeben:** Aktuell ausgegebene Schlüssel
- **Verfügbar:** Noch verfügbare Schlüssel

### Schlüssel zurücknehmen

#### 1. Vergabe finden
1. Admin-Bereich → Schlüsselvergaben
2. Nach aktiven Vergaben filtern (Rückgabedatum leer)
3. Entsprechende Vergabe auswählen

#### 2. Rückgabe dokumentieren
1. **Rückgabedatum** eintragen (Standard: heute)
2. **Bemerkungen** hinzufügen (z.B. "Zustand ok", "Beschädigt")
3. Speichern

#### 3. Kontrolle
- Schlüssel ist wieder verfügbar
- Historie ist vollständig dokumentiert

---

## Wichtige Administrationsaufgaben

### Neuen Schlüsseltyp anlegen
1. Admin-Bereich → Schlüsseltypen → Add
2. **Bezeichnung:** Eindeutiger Name
3. **Beschreibung:** Detaillierte Informationen
4. **Farbe:** Hex-Code für visuelle Unterscheidung
5. **Gesamtanzahl:** Anzahl der vorhandenen Schlüssel
6. **Reihenfolge:** Position in Listen
7. Speichern

### Neue Person anlegen
1. Admin-Bereich → Personen → Add
2. **Name:** Vollständiger Name
3. **Funktion:** Rolle im Verein (z.B. Hausmeister)
4. **E-Mail:** Kontaktadresse
5. **Telefon:** Telefonnummer
6. **Bemerkungen:** Zusätzliche Informationen
7. **Aktiv:** Häkchen setzen
8. Speichern

### Überfällige Rückgaben prüfen
1. Admin-Bereich → Schlüsselvergaben
2. Filter: Nur aktive Vergaben anzeigen
3. Nach Ausgabedatum sortieren
4. Personen kontaktieren bei überfälligen Rückgaben

---

## Sicherheitsrichtlinien

### Zugriffsberechtigungen
- Nur autorisierte Personen dürfen Schlüssel vergeben
- Admin-Zugang ist geschützt und wird protokolliert
- Jede Aktion wird mit Zeitstempel dokumentiert

### Dokumentationspflicht
- Jede Ausgabe muss sofort dokumentiert werden
- Rückgaben sind zeitnah zu erfassen
- Bemerkungen bei besonderen Vorkommnissen

### Kontrollen
- Regelmäßige Überprüfung der Schlüsselbestände
- Monatliche Prüfung der offenen Vergaben
- Jährliche Inventur aller Schlüssel

---

## Berichte und Auswertungen

### Aktuelle Bestände
- Admin-Bereich → Schlüsseltypen
- Übersicht aller verfügbaren Schlüssel
- Farbcodierung für schnelle Erkennung

### Vergabe-Historie
- Admin-Bereich → Schlüsselvergaben
- Chronologische Liste aller Zuweisungen
- Filter nach Datum, Person oder Schlüsseltyp

### Offene Vergaben
- Filter auf aktive Vergaben
- Sortierung nach Ausgabedatum
- Identifikation überfälliger Rückgaben

---

## Fehlerbehebung

### Häufige Probleme

**"Schlüssel nicht verfügbar"**
- Prüfen ob alle Schlüssel zurückgegeben sind
- Gesamtanzahl im Schlüsseltyp überprüfen
- Ggf. neue Schlüssel anlegen

**"Person nicht gefunden"**
- Prüfen ob Person aktiv geschaltet ist
- Neue Person anlegen falls erforderlich
- Schreibweise des Namens überprüfen

**"Rückgabe nicht möglich"**
- Vergabe-ID überprüfen
- Sicherstellen dass richtige Vergabe ausgewählt ist
- Admin kontaktieren bei Systemproblemen

---

## Mobile Nutzung

### Responsive Design
- Anwendung funktioniert auf Tablets und Smartphones
- Touch-optimierte Bedienung
- Schnelle Erfassung von Ausgaben/Rückgaben

### Empfehlungen für den mobilen Einsatz
- Tablet für die tägliche Arbeit verwenden
- WLAN-Verbindung für stabile Nutzung
- Browser-Lesezeichen für schnellen Zugriff

---

## Technische Informationen

### Systemanforderungen
- Webbrowser mit JavaScript-Unterstützung
- Internetverbindung
- Admin-Berechtigung

### Browser-Unterstützung
- Chrome (aktuellste Version)
- Firefox (aktuellste Version)
- Safari (aktuellste Version)
- Edge (aktuellste Version)

### Datenbackup
- Regelmäßige Backups der Datenbank
- Export-Funktion für wichtige Daten
- Aufbewahrungspflicht beachten

---

## Best Practices

### Tägliche Arbeit
- Morgens: Prüfung der geplanten Ausgaben
- Laufeend: Sofortige Dokumentation
- Abends: Kontrolle der Rückgaben

### Wöchentliche Kontrollen
- Überprüfung offener Vergaben
- Kontakt mit überfälligen Rückgaben
- Aktualisierung der Kontaktdaten

### Monatliche Aufgaben
- Vollständige Inventur
- Prüfung der Schlüsselbestände
- Aktualisierung der Personenliste

---

## Notfallprozeduren

### Schlüsselverlust
1. Sofort dokumentieren (Bemerkungsfeld)
2. Person schriftlich informieren
3. ggf. Schloss austauschen lassen
4. Schlüsseltyp anpassen (Gesamtanzahl reduzieren)

### Systemausfall
1. Manuelle Dokumentation auf Papier
2. Nach Wiederherstellung: Nachtragung ins System
3. Admin informieren

### Unbefugte Nutzung
1. Sofortige Sperrung der Person
2. Alle Schlüssel zurückfordern
3. Vorfall dokumentieren
4. Vereinsleitung informieren

---

## Support und Hilfe

### Technischer Support
Bei Systemproblemen:
- IT-Abteilung des Vereins
- Screenshot des Fehlers machen
- Browser und Version angeben

### Inhaltliche Fragen
Bei organisatorischen Fragen:
- Schlüsselverwalter
- Hausmeister
- Vereinsleitung

---

## Rechtliche Hinweise

### Haftung
- Der Verein haftet für ordnungsgemäße Verwahrung
- Personen haften für überlassene Schlüssel
- Bei Verlust können Kosten entstehen

### Datenschutz
- Personen Daten werden vertraulich behandelt
- Speicherung nur für vereinbarte Zwecke
- DSGVO-konforme Verarbeitung

---

*Letzte Aktualisierung: April 2026*
