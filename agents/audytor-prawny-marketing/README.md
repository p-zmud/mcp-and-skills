# audytor-prawny-marketing

Subagent, który sprawdza treść pod kątem **prawa polskiego i unijnego, zanim pójdzie
w świat**, i wydaje werdykt: blokuje publikację, do poprawy, można publikować.

Obsługuje pytania, o które realnie rozbija się marketing: czy ten post jest oznaczony
jako reklama, czy mamy prawa do tego zdjęcia i tego utworu, czy polityka prywatności ma
komplet elementów z art. 13 RODO, czy ten „konkurs" nie jest przypadkiem loterią, czy
w regulaminie sklepu nie siedzi klauzula abuzywna, czy cena promocyjna spełnia wymóg
najniższej ceny z 30 dni.

Werdykt jest po polsku, prostym językiem - poprawki mają się nadawać do wklejenia
wprost w treść.

> To nie jest porada prawna. Agent nie jest prawnikiem i nigdy się za niego nie podaje;
> każdy werdykt kończy się stopką, która to mówi. Traktuj go jak filtr przedpublikacyjny,
> który wyłapuje rzeczy oczywiste i kosztowne - nie jak zamiennik prawnika przy czymkolwiek
> istotnym.

## Czym to się różni od zapytania modelu „czy to jest legalne?"

Modele halucynują prawo z pełnym przekonaniem - mierzone wskaźniki halucynacji na
zapytaniach prawnych sięgają od 17% do ponad 75%, a dominujący tryb porażki to zacytowanie
**prawdziwego** przepisu z przekłamaną treścią. Ten agent jest zbudowany wokół tego
jednego problemu:

- **Żaden przepis nie wchodzi do werdyktu, jeśli jego źródło nie zostało otwarte w tym
  przebiegu.** Numer artykułu z pamięci modelu jest zakazany, niezależnie od tego, jak
  bardzo model jest pewny.
- **Sprawdzana jest treść przepisu, nie samo jego istnienie** - agent czyta pobrany tekst
  i w werdykcie pisze jednym zdaniem, co ten przepis faktycznie mówi.
- **Weryfikowany jest stan obowiązywania** - akty uchylone, znowelizowane, zawetowane
  i takie, które jeszcze nie weszły w życie, to standardowa pułapka. Checklisty wymieniają
  te aktualne wprost (PKE w miejsce Prawa telekomunikacyjnego, zawetowana polska ustawa
  o DSA, etapowy harmonogram AI Act, nowelizacja prawa autorskiego z 2024, Omnibus, EAA,
  dyrektywa 2024/825 o greenwashingu).
- **Ustalone prawo jest oddzielone od interpretacji.** Sekcja A werdyktu to to, co mówią
  źródła; ocena ryzyka jest opisana jako ocena.
- **Ryzyko platformy to osobna sekcja.** Polityki reklamowe Meta/TikTok/Google i licencje
  ZAiKS/STOART wywalają post równie skutecznie co ustawa, ale nie są prawem i nigdy nie są
  jako prawo podawane.
- **Orzeczenia tylko z SAOS, CBOSA, SN albo CURIA**, otwarte w tym przebiegu. Blog
  kancelarii służy do namierzenia przepisu, nigdy jako podstawa werdyktu.

## Instalacja

```bash
# w Claude Code
/plugin marketplace add p-zmud/mcp-and-skills
/plugin install audytor-prawny-marketing@pzmud
```

## Użycie

Deleguj do agenta i podaj trzy rzeczy: **co** audytujesz (ścieżka pliku albo sama treść),
**kanał publikacji** i **branżę**. Bez treści agent zatrzymuje się i o nią prosi.

```
Użyj agenta audytor-prawny-marketing na drafts/post-instagram.md - Instagram Reels,
marka suplementów, płatna współpraca z twórcą.
```

```
Użyj agenta audytor-prawny-marketing na tej stopce newslettera - e-mail, e-commerce.
```

Dobre momenty na wywołanie: przed publikacją każdej treści płatnej lub brandowanej, przed
startem konkursu, przed wdrożeniem regulaminu, polityki prywatności, banera cookies albo
disclaimera, przed podpisaniem umowy z klientem.

Werdykt wraca w czterech sekcjach:

| Sekcja | Co zawiera |
| ------ | ---------- |
| A. Naruszenia prawa | Per pozycja: cytat fragmentu, waga naruszenia, podstawa prawna z URL-em, który agent otworzył, jedno zdanie o tym, co przepis mówi, i gotowa poprawka do wklejenia |
| B. Ryzyko platformy | Polityki reklamowe, licencje muzyczne - jawnie oznaczone jako nie-prawo |
| C. Niezweryfikowane | Czego nie dało się potwierdzić i dlaczego, plus pytania blokujące |
| D. Sprawdzone i czyste | Co przeszło audyt, żeby było widać jego zakres |

## Co jest w tym pluginie

```
agents/audytor-prawny-marketing.md   subagent (Read, Grep, Glob, WebSearch, WebFetch, Skill)
skills/prawo-pl/SKILL.md             router: typ dokumentu -> checklista, plus rejestr źródeł
skills/prawo-pl/references/          siedem checklist, wczytywanych tylko gdy pasują do dokumentu
```

Skill `prawo-pl` jest dołączony do pluginu, a nie wydany osobno: agent bez niego jest
bezużyteczny, a checklista bez dyscypliny weryfikacyjnej agenta to szybka droga do pewnej
siebie błędnej odpowiedzi. `SKILL.md` jest routerem - wczytuje jedną do trzech checklist
na audyt zamiast wszystkich 48 KB naraz.

| Checklista | Zakres |
| ---------- | ------ |
| `zrodla-i-weryfikacja.md` | Wczytywana zawsze jako pierwsza: jak zweryfikować przepis, kiedy odmówić jego podania, jak rozdzielić ustalone prawo od oceny |
| `content-social-reklama.md` | Czy treść jest komercyjna, oznaczenie reklamy, sam przekaz, treści z AI, twórca wideo jako dostawca usługi medialnej, kiedy blog jest prasą |
| `prawo-autorskie-wizerunek.md` | Pochodzenie każdego elementu materiału, cytat i dozwolony użytek, wizerunek, muzyka, materiały z AI, znaki towarowe, autorskie prawa osobiste |
| `polityka-prywatnosci-rodo.md` | Obowiązek informacyjny z art. 13, zgody na formularzach, marketing bezpośredni po PKE, cookies, dokumentacja administratora |
| `ecommerce-regulaminy.md` | Regulamin, identyfikacja sprzedawcy, odstąpienie, zgodność towaru i reklamacje, klauzule abuzywne, ceny i opinie po Omnibusie, dark patterns, dostępność cyfrowa, umowa agencji z klientem |
| `reklamy-regulowane.md` | Konkurs czy loteria, alkohol, tytoń i nikotyna, suplementy i żywność, leki i apteki, finanse i krypto, hazard, claimy środowiskowe, dzieci |
| `ryzyko-platform.md` | Polityki platform, muzyka i organizacje zbiorowego zarządzania, zasoby stockowe - trzymane poza sekcjami prawnymi |

Źródła pierwszego wyboru, z których agent pracuje: ISAP, ELI, API Sejmu i Dziennik Ustaw
dla prawa krajowego; EUR-Lex po CELEX dla prawa unijnego; SAOS, CBOSA, SN i CURIA dla
orzecznictwa; UOKiK, UODO, EDPB, KRRiT, KNF, URPL, GIF i UKE dla stanowisk organów.

## Uwagi

- `model: opus` - agent świadomie wybiera dokładność zamiast szybkości, a jeden przebieg
  dotyka wielu źródeł.
- Agent **nigdy nie edytuje plików**. Poprawki wracają jako tekst do wklejenia.
- Nie podpowie, jak obejść przepis - wskaże zgodny z prawem sposób osiągnięcia tego samego
  celu.
- Niepewność jest głośna: agent najpierw przeskanuje cały dokument, a potem zbiera wszystkie
  pytania blokujące w jednej wiadomości, zamiast zgadywać albo po cichu pominąć punkt.

## Licencja

MIT - patrz [korzeń repozytorium](https://github.com/p-zmud/mcp-and-skills).
