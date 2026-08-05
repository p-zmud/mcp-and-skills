# Źródła i weryfikacja - jak sprawdzać, zanim wpiszesz przepis do werdyktu

Ten plik czytasz **zawsze**, przed każdą checklistą merytoryczną.

## Zasada zero

**Nie cytujesz z pamięci. Nigdy.** Każdy numer artykułu, każda sygnatura, każda
data i każda kwota kary trafia do werdyktu dopiero po otwarciu źródła w TYM
przebiegu. Nie ma wyjątku dla przepisów „oczywistych" - art. 81 prawa autorskiego
i art. 13 RODO też otwierasz.

Powód nie jest teoretyczny. Zmierzone wskaźniki halucynacji na zapytaniach
prawnych: komercyjne narzędzia RAG dla prawników 17-34%, modele ogólne 58-82%,
a przy pytaniach o istotę rozstrzygnięcia sądu błąd w co najmniej 75% przypadków.
Dominujący tryb porażki: model trafia w numer przepisu i **przekłamuje jego
treść**. Samo pobranie dokumentu tego nie leczy - musisz przeczytać to, co
pobrałeś, i porównać z tym, co zamierzasz napisać.

## Procedura weryfikacji jednego przepisu

1. **Namierz** - jeśli nie wiesz, gdzie szukać, WebSearch albo blog kancelarii.
   To wyłącznie trop, nie źródło.
2. **Otwórz tekst aktu** - ISAP, ELI, `dziennikustaw.gov.pl` albo EUR-Lex.
   Pomocniczo `lexlege.pl` / `arslege.pl` do deep-linku na poziom artykułu, ale
   wtedy potwierdź w ISAP, bo te serwisy nie gwarantują aktualności.
3. **Przeczytaj brzmienie** i sformułuj jednym zdaniem, co przepis mówi. Jeśli
   nie umiesz tego zdania napisać z otwartego tekstu - nie masz podstawy.
4. **Sprawdź, czy obowiązuje**: czy jest tekst jednolity nowszy niż Twoje
   źródło, czy artykuł nie został uchylony, czy nowelizacja weszła w życie
   (vacatio legis!), czy akt w ogóle został podpisany i ogłoszony.
5. **Dopiero teraz** wpisz do werdyktu w formacie ze SKILL.md.

## Kiedy szukasz szczególnie ostrożnie

- Przepis, który „pamiętasz" z Prawa telekomunikacyjnego, uśude albo starego
  prawa autorskiego - te obszary przeorano po 2024 r.
- Wszystko, co dotyczy AI, platform internetowych, dostępności i greenwashingu -
  legislacja w ruchu.
- Kwoty kar i progi - najczęściej przepisywane błędnie z artykułów prasowych.
- Ustawa, o której źródła mówią „uchwalona" albo „podpisana" - to nie znaczy,
  że obowiązuje. Sprawdź datę wejścia w życie w przepisach końcowych.

## Weryfikacja orzeczenia

Sygnatura bez otwartego orzeczenia jest zabroniona. Bazy: SAOS, CBOSA
(`orzeczenia.nsa.gov.pl/cbo/query`), SN, CURIA, decyzje UODO
(`orzeczenia.uodo.gov.pl/search`), decyzje UOKiK (`decyzje.uokik.gov.pl`).
Przy decyzjach UOKiK zaznacz, czy są prawomocne - od decyzji przysługuje
odwołanie do SOKiK.

## Gdy nie da się zweryfikować

Nie zgaduj i nie pomijaj po cichu. Masz dwie ścieżki:

- **Punkt nieistotny dla werdyktu** → sekcja C werdyktu: „nie potwierdziłem
  X, bo Y; wpływ na ocenę: żaden / potencjalny".
- **Punkt materialny dla werdyktu** → dokończ skan całego dokumentu, a potem
  zakończ turę jedną wiadomością z kompletem pytań blokujących i tą częścią
  audytu, którą udało się domknąć. Nie masz narzędzia do zadawania pytań -
  zwracasz je orkiestratorowi, który przekaże je właścicielowi.

Typowe przyczyny, dla których źródło nie odpowiada: ISAP za CAPTCHA (użyj ELI
albo API Sejmu), PDF za duży, serwis zwraca 403. To NIE jest powód, żeby zacytować
z pamięci - to powód, żeby zmienić źródło albo zgłosić brak weryfikacji.

## Rozdzielenie warstw w werdykcie

- **USTALONE PRAWO** - to, co przeczytałeś w otwartym źródle. Cytuj wiernie.
- **OCENA RYZYKA** - Twoja interpretacja, jak organ mógłby zakwalifikować
  konkretną treść. Zawsze oznaczona jako ocena, nigdy jako brzmienie przepisu.
- **RYZYKO PLATFORMY** - regulaminy prywatnych firm. Osobna sekcja B, nigdy
  wymieszana z prawem.

## Czego nie robisz

- Nie cytujesz `ictlaw.pl` - ta domena nie istnieje.
- Nie odsyłasz do rejestru klauzul niedozwolonych UOKiK jak do wiążącej listy -
  od 18.04.2026 to zanonimizowane archiwum edukacyjne.
- Nie traktujesz projektów i zapowiedzi (Digital Fairness Act, Digital Omnibus,
  projekty MZ o suplementach) jak obowiązującego prawa. Możesz o nich wspomnieć
  w sekcji C jako o nadchodzącej zmianie, z wyraźnym „to projekt".
- Nie przedstawiasz się jako prawnik, adwokat, radca prawny ani kancelaria.
