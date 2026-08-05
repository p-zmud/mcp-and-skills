# ksef

Serwer MCP do **KSeF API 2.0** - Krajowego Systemu e-Faktur. Wystawianie i pobieranie faktur,
kwerendy metadanych, uprawnienia, certyfikaty, tokeny, kody QR i tryby offline: **54 narzędzia
pokrywające wszystkie 83 operacje API**.

Rozmawiasz z Claude zwykłym językiem („pokaż faktury z lipca", „wystaw fakturę dla firmy X"),
a on sam dobiera narzędzia.

## To nie jest wtyczka Claude Code

W tym katalogu leży **gotowa paczka `.mcpb`** - rozszerzenie Claude Desktop, nie plugin do
`/plugin install`. Instaluje się dwuklikiem, nie wymaga Node.js ani edycji plików
konfiguracyjnych: cały serwer wraz z zależnościami jedzie w środku (8,3 MB).

```
ksef-mcp-0.1.0.mcpb   paczka do instalacji w Claude Desktop
INSTRUKCJA.md         instrukcja krok po kroku dla osoby nietechnicznej
INSTRUKCJA.pdf        ta sama instrukcja do druku
manifest.json         co paczka deklaruje: wymagane pola konfiguracji, wersje, uprawnienia
```

Pobierz `.mcpb`, kliknij dwukrotnie, wypełnij formularz. Jeśli dwuklik nic nie robi:
**Ustawienia → Rozszerzenia → Zainstaluj rozszerzenie** i wskaż plik. Pełna wersja z obrazkami
problemów w [INSTRUKCJA.md](INSTRUKCJA.md).

## Konfiguracja: pięć pól

Po instalacji Claude Desktop pyta o pięć rzeczy (opisy pochodzą z `manifest.json`):

| Pole | Co wpisać |
| ---- | --------- |
| **Środowisko KSeF** | `TEST` na naukę (dane fikcyjne), `DEMO` na prawdziwe poświadczenia bez skutków, `PRD` to produkcja. Zaczynaj od `TEST`. |
| **NIP podmiotu** | 10 cyfr bez myślników. |
| **Token KSeF** | Generujesz w aplikacji KSeF, zakładka Tokeny, osobno dla każdego środowiska. Pole oznaczone jako `sensitive`, więc trafia do keychaina systemu, nie do pliku. |
| **Zakres uprawnień** | `read-only` albo `full`. Przy `read-only` każda próba zapisu zostaje odrzucona z czytelnym komunikatem. |
| **Katalog na pliki** | Opcjonalny. Tu lądują XML-e faktur, UPO, PDF-y i klucze certyfikatów. Domyślnie `~/.ksef-mcp`. |

Token z `TEST` nie zadziała na produkcji i odwrotnie. Pokazuje się jeden raz przy generowaniu,
więc skopiuj go od razu.

## Co potrafi

54 narzędzia w dziewięciu grupach:

| Grupa | Zakres |
| ----- | ------ |
| **Uwierzytelnianie i sesja** | logowanie tokenem, certyfikatem `.p12` albo gotowym XAdES, status sesji, wylogowanie, unieważnianie sesji |
| **Wysyłka** | faktury FA(3): budowanie, walidacja, wysyłka pojedyncza, sesje interaktywne i wsadowe, UPO |
| **Pobieranie** | pobieranie faktur i UPO, kwerendy metadanych, eksporty, renderowanie do PDF |
| **Uprawnienia** | nadawanie i odbieranie uprawnień: osoby, podmioty, podmioty unijne, pośrednie, jednostki podrzędne |
| **Certyfikaty KSeF** | wniosek, status, pobranie, unieważnienie, limity |
| **Tokeny KSeF** | tworzenie, lista, status, unieważnianie |
| **Identyfikatory zbiorcze** | generowanie i kwerendy |
| **Pomocnicze** | klucze publiczne, kody QR, tryb offline, limity, dostawcy Peppol, status operacji |
| **Dane testowe** | tworzenie podmiotów, osób i uprawnień - istnieje wyłącznie na środowisku `TEST` |

Pełna referencja z opisem każdego narzędzia (`docs/narzedzia.md`) i mapowanie 83 operacji API na
narzędzia (`docs/mapowanie-api.md`) jedzie w paczce.

## Zanim wpiszesz PRD

Dwie rzeczy do świadomej decyzji, obie opisane szerzej w `docs/bezpieczenstwo.md` w paczce:

- **Treść faktur trafia do Anthropic.** Kiedy poprosisz o zawartość faktury, jej dane - łącznie
  z nazwą, NIP-em, adresem i kwotami kontrahenta - stają się częścią rozmowy i lądują na
  serwerach Anthropic. To nie jest właściwość tego serwera, tylko każdej rozmowy z modelem.
  Jeśli potrzebujesz zestawienia, proś o listę faktur zamiast o ich treść: wtedy przechodzą same
  numery, daty i kwoty.
- **Na produkcji faktura jest nieodwracalna.** Zakres `full` na `PRD` znaczy, że Claude może
  wystawić prawdziwą fakturę ze skutkiem prawnym. Serwer trzyma na produkcji dwa niezależne
  bezpieczniki, ale najprostszy z nich to wpisanie `read-only`, dopóki nie jesteś gotów.

## Uwagi

- **Wymagania:** Claude Desktop `>=0.10.0`. Runtime Node 20+ jest w paczce, nie musisz go mieć.
  Działa na macOS, Windows i Linuksie.
- **Odinstalowanie:** Ustawienia → Rozszerzenia → KSeF → usuń. Token znika z keychaina razem
  z rozszerzeniem.
- **Linki w `manifest.json`** (`homepage`, `documentation`) prowadzą do repozytorium źródłowego,
  które nie jest publiczne. Komplet dokumentacji - bezpieczeństwo, uwierzytelnianie, przykłady,
  rozwiązywanie problemów, referencja narzędzi - jest w katalogu `docs/` **wewnątrz paczki**.
- Paczka to artefakt budowania. Wersja tutaj to `0.1.0`; kod źródłowy serwera nie wchodzi do
  tego repozytorium.

## Licencja

MIT.

Bez gwarancji i bez wsparcia, używasz na własną odpowiedzialność - autor nie ponosi
odpowiedzialności za żadne szkody, utratę danych, błędnie wystawione faktury ani skutki
podatkowe czy prawne użycia tego narzędzia. To nie jest doradztwo podatkowe ani księgowe.
Przed pracą na środowisku produkcyjnym sprawdź wszystko na `TEST`.
