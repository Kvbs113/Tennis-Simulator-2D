# Tennis Simulator 

**Tennis Simulator** to retro-arkadowa gra sportowa 2D z elementami perspektywy 3D, napisana w języku Python przy użyciu biblioteki **Pygame**. Gra łączy klasyczną rozgrywkę tenisową z nowoczesnymi mechanikami, takimi jak unikalne superumiejętności postaci (Ulty), zróżnicowane statystyki zawodników oraz zaawansowany model fizyki piłki (uwzględniający wysokość, opór powietrza oraz rotację).

---

##  Kluczowe Funkcje

* **Zaawansowana Fizyka Piłki:** Symulacja lotu piłki w trzech wymiarach (X, Y oraz wysokość Z) z uwzględnieniem grawitacji, oporu powietrza, cieniowania oraz mechaniki nadawania rotacji (*spin*).
* **4 Grywalne Postacie:** * *Nowicjusz* (Ult: Nietykalność – ignoruje błędy)
    * *Amator* (Ult: Nitro – potężny bonus do prędkości biegu)
    * *Pro* (Ult: Dotlenienie – zwiększona dynamika)
    * *Mistrz* (Ult: Polska gurom – potrójny zasięg odbicia piłki)
* **4 Poziomy Trudności AI:** Od relaksującego poziomu Łatwego, przez Średni i Trudny, aż po bezbłędny tryb Ekspert o nieludzkim tempie gry.
* **Tryb Turniejowy (Wimbledon):** Drabinka pucharowa składająca się z 4 rund o rosnącym poziomie trudności. Jeden przegrany mecz oznacza eliminację z turnieju!
* **Dynamiczny System Animacji:** Proceduralne oraz spritowe renderowanie zawodników i rakiet podążających za dłonią gracza.
* **Pełna Dokumentacja Techniczna:** Kod źródłowy w pełni zintegrowany z systemem generatora dokumentacji **Sphinx** wraz z automatycznymi diagramami klas UML.

---

##  Sterowanie

| Klawisz | Akcja |
| :--- | :--- |
| `W`, `A`, `S`, `D` / `↑`, `↓`, `←`, `→` | Poruszanie się po swojej połowie kortu |
| `SPACJA` (faza serwisu) | Pierwsze wciśnięcie: podrzut piłki / Drugie wciśnięcie: uderzenie |
| `SPACJA` (faza wymiany) | Uderzenie piłki rakietą (gdy piłka jest w zasięgu) |
| `A` / `D` lub `←` / `→` | Nadanie piłce rotacji w lewo/prawo (w momencie uderzenia) |
| `Q` | Aktywacja unikalnej superumiejętności (Ult) |
| `ESC` | Powrót do menu głównego / Wyjście |

---

##  Instalacja i Uruchomienie

### Wymagania
Do uruchomienia gry wymagany jest zainstalowany **Python 3.8+** oraz menedżer pakietów **pip**.

### Szybki start
1. Sklonuj repozytorium lub pobierz paczkę ZIP z projektem.
2. Otwórz terminal/konsolę w głównym folderze projektu.
3. Zainstaluj bibliotekę Pygame (zalecana wersja `pygame-ce`):
```bash
pip install pygame
