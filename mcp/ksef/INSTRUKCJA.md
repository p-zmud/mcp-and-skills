# KSeF w Claude - instalacja

Dostałeś jeden plik: `ksef-mcp-0.1.0.mcpb`. Nie musisz nic instalować poza samym
Claude Desktop - żadnego Node.js, żadnej edycji plików konfiguracyjnych.

## 1. Instalacja (30 sekund)

**Sposób prostszy:** kliknij dwukrotnie plik `ksef-mcp-0.1.0.mcpb`.
Claude Desktop otworzy okno instalacji.

**Jeśli dwuklik nic nie robi:** otwórz Claude Desktop, wejdź w
**Ustawienia → Rozszerzenia**, kliknij **Zainstaluj rozszerzenie** i wskaż ten plik.

## 2. Konfiguracja (formularz, 4 pola)

Po instalacji zobaczysz formularz. Wypełnij go tak:

| Pole | Co wpisać |
|---|---|
| **Środowisko KSeF** | `TEST` na początek. Zmienisz na `PRD`, gdy będziesz gotów na prawdziwe faktury. |
| **NIP podmiotu** | 10 cyfr bez myślników, NIP Twojej firmy. |
| **Token KSeF** | Patrz punkt 3 poniżej. |
| **Zakres uprawnień** | `full` jeśli Claude ma wystawiać faktury, `read-only` jeśli ma tylko czytać. |

Piąte pole (katalog na pliki) możesz zostawić puste.

Kliknij **Zapisz** i włącz rozszerzenie przełącznikiem.

## 3. Skąd wziąć token KSeF

Token to długi ciąg znaków, który zastępuje hasło.

1. Wejdź na stronę KSeF dla wybranego środowiska:
   - TEST: **https://ksef-test.mf.gov.pl**
   - Produkcja: **https://ksef.mf.gov.pl**
2. Zaloguj się Profilem Zaufanym albo podpisem kwalifikowanym.
3. Wybierz kontekst - NIP swojej firmy.
4. Wejdź w zakładkę **Tokeny** i wygeneruj nowy.
5. Zaznacz uprawnienia:
   - do samego przeglądania faktur wystarczy **InvoiceRead**;
   - do wystawiania faktur potrzebujesz też **InvoiceWrite**.
6. **Skopiuj token natychmiast** - pokazuje się tylko raz i nie da się go
   odczytać ponownie.

Token jest przypisany do środowiska. Token wygenerowany na TEST **nie zadziała**
na produkcji i odwrotnie.

Twój token trafia do keychaina systemu (Pęk kluczy na macOS, Menedżer poświadczeń
na Windowsie), a nie do zwykłego pliku tekstowego.

## 4. Sprawdź, czy działa

Otwórz nową rozmowę i napisz:

> Na jakim środowisku KSeF jestem?

Claude powinien odpowiedzieć, że TEST i że jest zalogowany na Twój NIP.

## 5. Co możesz robić

Piszesz zwykłym językiem, Claude sam dobiera narzędzia.

**Przeglądanie:**

> Pokaż faktury, które dostałem w lipcu.

> Ile wystawiłem w zeszłym miesiącu i dla kogo?

> Pokaż mi całą treść faktury o numerze KSeF 1234567890-...

> Zrób z tej faktury PDF.

**Wystawianie:**

> Wystaw fakturę FV/2026/08/001 dla firmy Przykład sp. z o.o., NIP 1234567890,
> adres ul. Marszałkowska 1, 00-001 Warszawa. Jedna pozycja: usługa doradcza,
> 10 godzin po 200 zł netto, VAT 23%.

Dostaniesz numer KSeF i UPO, czyli urzędowe potwierdzenie.

**Uprawnienia:**

> Nadaj Annie Kowalskiej, PESEL 12345678901, uprawnienia do czytania faktur.

Więcej scenariuszy: plik `docs/przyklady.md` w paczce.
Spis wszystkich 54 narzędzi: `docs/narzedzia.md`.

## 6. Zanim wpiszesz PRD

Dwie rzeczy warte świadomej decyzji.

**Faktury trafiają do Anthropic.** Kiedy poprosisz o treść faktury, jej zawartość -
w tym dane kontrahenta: nazwa, NIP, adres, kwoty - staje się częścią rozmowy
i trafia na serwery Anthropic. To jest niezależne od tego narzędzia i dotyczy
każdej rozmowy z Claude. Jeśli potrzebujesz tylko zestawienia, poproś o listę
faktur zamiast o ich treść - wtedy przechodzą same numery, daty i kwoty.

**Na produkcji faktura jest nieodwracalna.** Zakres `full` na środowisku `PRD`
oznacza, że Claude może wystawić prawdziwą fakturę ze skutkiem prawnym. Jeśli chcesz
najpierw popatrzeć, wpisz `read-only` - wtedy każda próba zapisu zostanie odrzucona
z czytelnym komunikatem.

Pełny opis: `docs/bezpieczenstwo.md` w paczce.

## 7. Gdy coś nie działa

| Objaw | Co zrobić |
|---|---|
| Rozszerzenia nie widać po instalacji | zamknij Claude Desktop całkowicie (na Macu Cmd+Q) i uruchom ponownie |
| "Brak aktywnej sesji KSeF" | sprawdź token i NIP w Ustawieniach → Rozszerzenia |
| "Nie udało się zalogować" | najczęściej token z innego środowiska niż wybrane |
| Faktura odrzucona, kod 450 | brakuje adresu sprzedawcy albo nabywcy - podaj go w poleceniu |
| Nie widać narzędzi do danych testowych | to normalne, istnieją tylko na środowisku TEST |

Więcej: `docs/rozwiazywanie-problemow.md` w paczce.

## Odinstalowanie

Ustawienia → Rozszerzenia → KSeF → usuń. Token znika z keychaina razem
z rozszerzeniem.
