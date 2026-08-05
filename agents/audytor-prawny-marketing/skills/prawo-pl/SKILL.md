---
name: prawo-pl
description: >-
  Zaplecze checklist i źródeł prawnych (oznaczanie reklamy, prawo autorskie
  i wizerunek, RODO i cookies, regulaminy i klauzule abuzywne, e-commerce
  i Omnibus, konkursy vs loterie, branże regulowane) dla subagenta
  `audytor-prawny-marketing`. ⚠ NIE wywołuj tego skilla, żeby samemu zaudytować treść -
  prośby typu „sprawdź ten post przed publikacją", „czy mogę to opublikować",
  „sprawdź regulamin / politykę prywatności / disclaimer", „czy to legalne"
  deleguj do subagenta `audytor-prawny-marketing`, który ma dyscyplinę weryfikacji
  źródeł, wymuszony format werdyktu i disclaimer. Ten skill wczytuj sam tylko
  wtedy, gdy potrzebujesz punktowo namierzyć źródło albo przepis bez
  wydawania werdyktu.
---

# prawo-pl - checklisty audytu

Ten plik to **router**. Ciężkie checklisty leżą w `references/` i wczytujesz je
`Read`em dopiero po rozpoznaniu typu dokumentu.

## Router: typ dokumentu → plik

| Co audytujesz | Wczytaj |
|---|---|
| Zawsze, jako pierwsze | `references/zrodla-i-weryfikacja.md` |
| Post, rolka, stories, kampania, współpraca, ambasador, autopromocja, treść z AI | `references/content-social-reklama.md` |
| Cudze zdjęcia, grafiki, teksty, muzyka, wizerunek osób, cytat, mem, prawa do materiału AI | `references/prawo-autorskie-wizerunek.md` |
| Polityka prywatności, formularz, newsletter, cookie banner, profilowanie, zgody | `references/polityka-prywatnosci-rodo.md` |
| Regulamin serwisu lub sklepu, karta produktu, promocja, opinie, treści cyfrowe, umowa z klientem | `references/ecommerce-regulaminy.md` |
| Alkohol, piwo, tytoń i nikotyna, suplementy, żywność, leki, apteki, wyroby medyczne, finanse i krypto, hazard, konkurs z nagrodami, claimy eko | `references/reklamy-regulowane.md` |
| Ryzyko wyrzucenia posta lub odrzucenia reklamy, licencje muzyczne, ZAiKS/STOART | `references/ryzyko-platform.md` |

Ścieżki są względem katalogu tego skilla - jeśli startujesz w innym katalogu
roboczym, złóż ścieżkę bezwzględną z lokalizacji tego pliku. Typowy post
sponsorowany dotyka zwykle 3 plików naraz (content + autorskie + platformy) -
wczytaj wszystkie właściwe, nie tylko pierwszy z brzegu.

## Rejestr źródeł pierwszego wyboru

**Prawo krajowe**
- ISAP: `https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU{RRRR}{POZ:7 cyfr}` - np. `WDU20240001254`. Bywa za CAPTCHA przy fetchu.
- ELI (fallback ISAP-u, stabilne linki): `https://eli.gov.pl/eli/DU/{rok}/{poz}/ogl` (`tj` = tekst jednolity, `uj` = ujednolicony).
- API Sejmu: `https://api.sejm.gov.pl/eli/acts/DU/{rok}/{poz}/text.pdf`.
- Dziennik Ustaw: `https://dziennikustaw.gov.pl/DU/{rok}/{poz}`.
- Czy już obowiązuje: `https://www.sejm.gov.pl/Sejm10.nsf/PrzebiegProc.xsp?nr={druk}`.
- Szybki deep-link do artykułu (pomocniczo, NIE jako jedyne źródło): `lexlege.pl`, `arslege.pl`.

**Prawo UE**
- EUR-Lex po CELEX: `https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:{celex}` - RODO `32016R0679`, DSA `32022R2065`, DMA `32022R1925`, AI Act `32024R1689`, Data Act `32023R2854`, Empowering Consumers `32024L0825`.

**Orzecznictwo** - SAOS `saos.org.pl`, NSA/WSA `orzeczenia.nsa.gov.pl/cbo/query`, SN `sn.pl/orzecznictwo`, TSUE `curia.europa.eu`, UODO `orzeczenia.uodo.gov.pl/search`, UOKiK `decyzje.uokik.gov.pl`.

**Organy i soft law** - UOKiK `uokik.gov.pl` (+ `uokik.gov.pl/influencer-marketing`, `uokik.gov.pl/bip/wyjasnienia`, archiwum `archiwum.uokik.gov.pl`), UODO `uodo.gov.pl`, EDPB `edpb.europa.eu`, KRRiT `gov.pl/web/krrit`, KNF `knf.gov.pl`, URPL `gov.pl/web/urpl`, GIF `gov.pl/web/gif`, UKE `uke.gov.pl`, Rada Reklamy `radareklamy.pl/kodeks-etyki-reklamy_new/`, Ministerstwo Cyfryzacji `gov.pl/web/cyfryzacja`.

**Śledzenie zmian** - `prawo.pl`, `traple.pl/blog/`, `panoptykon.org`. Zawsze jako trop, nigdy jako podstawa.

## Hierarchia źródeł

tekst aktu w ISAP/ELI/EUR-Lex **>** wytyczne organu **>** orzecznictwo **>**
komentarz kancelarii. Blog kancelarii służy WYŁĄCZNIE do namierzenia przepisu,
który potem otwierasz w ISAP. Nigdy nie jest samodzielną podstawą w werdykcie.

## Format cytatu w werdykcie (jeden wzór, bez wariantów)

```
art. 7 pkt 11 ustawy z 23.08.2007 r. o przeciwdziałaniu nieuczciwym praktykom
rynkowym (Dz.U. 2007 nr 171 poz. 1206 ze zm.)
  źródło: https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20071711206
  co mówi: kryptoreklama jest praktyką nieuczciwą w każdych okolicznościach.
```

Nie ma numeru artykułu bez URL-a, który otworzyłeś. Nie ma URL-a bez zdania
o tym, co przepis faktycznie mówi.

## Pułapki - tu wiedza modelu jest najczęściej nieaktualna

Każdy z tych punktów sprawdź w źródle, zanim cokolwiek napiszesz:

1. **Prawo telekomunikacyjne już nie obowiązuje.** Zastąpiło je PKE (Dz.U. 2024 poz. 1221) od 10.11.2024. Marketing bezpośredni to art. 398 PKE, a art. 10 uśude został uchylony.
2. **Nie ma polskiej ustawy wdrażającej DSA.** Prezydent zawetował ją 9.01.2026, projekt podzielono na dwa - status sprawdzaj w Sejmie przed każdą wzmianką. Samo rozporządzenie DSA stosuje się bezpośrednio od 17.02.2024.
3. **AI Act ma harmonogram etapowy.** Obowiązki przejrzystości z art. 50 (chatboty, deepfake, treści syntetyczne) obowiązują od 2.08.2026. Polska ustawa o systemach AI podpisana 24.07.2026 - datę wejścia w życie i numer Dz.U. zweryfikuj.
4. **Prawo autorskie po nowelizacji z 26.07.2024** (Dz.U. 2024 poz. 1254, w życie 20.09.2024) - wdrożenie DSM, nowe art. 26(2) i 26(3) o eksploracji tekstów i danych.
5. **Rejestr klauzul niedozwolonych UOKiK od 18.04.2026 jest tylko zanonimizowanym archiwum edukacyjnym.** Wiążące są decyzje Prezesa UOKiK - `decyzje.uokik.gov.pl`.
6. **Omnibus** (od 1.01.2023): najniższa cena z 30 dni, weryfikacja opinii, przejrzystość plasowania.
7. **European Accessibility Act** - ustawa z 26.04.2024 (Dz.U. 2024 poz. 731) obowiązuje od 28.06.2025 i obejmuje sklepy internetowe i aplikacje.
8. **Greenwashing** - dyrektywa 2024/825 stosowana od 27.09.2026; stan polskiej implementacji sprawdź, nie zakładaj.
9. **ePrivacy jako rozporządzenie nie powstanie** - projekt wycofany 11.02.2025. Cookies: dyrektywa 2002/58/WE przeniesiona do PKE + RODO.
10. **Reżim reklamy aptek jest w trakcie zmiany** po wyroku TSUE z 2025 - "całkowity zakaz" może być już nieaktualny.

Data w Twojej głowie nie jest aktualną datą. Jeśli przepis mógł się zmienić po
Twoim cutoffie, sprawdź go, nawet gdy „pamiętasz" brzmienie.
