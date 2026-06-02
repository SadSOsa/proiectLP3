
import os, json, argparse, datetime

# Numele fisierului unde salvam maparea vechi->nou (pentru undo)
UNDO = ".undo.json"

def redenumeste(director, sablon):
    # protectie in cazul in care exista deja un .undo.json (daca se ruleaza,practic se suprascriu denumirile originale)
    if os.path.exists(os.path.join(director, UNDO)):
        print("ATENTIE!!: Exista deja o redenumire anterioara nesalvata!")
        print("Folositi --undo pentru a restaura fisierele inainte de o noua redenumire.")
        if input("Continuati oricum? (da/nu): ").strip().lower() not in ("da", "d"):
            print("Anulat.Foloseste --undo mai intai.")
            return

    #Listam doar fisierele vizibile (fara cele ascunse care incep cu "."), sortate alfabetic
    fisiere = sorted(f for f in os.listdir(director)
                     if os.path.isfile(os.path.join(director, f)) and not f.startswith("."))
    if not fisiere:
        print("Nu s-au gasit fisiere.")
        return

    data = datetime.datetime.now().strftime("%Y-%m-%d")  # Data curenta pt variabila {data}
    mapare = {}  # Dictionar: nume_vechi -> nume_nou
    print(f"\nDirector: {os.path.abspath(director)}\nSablon:   {sablon}\n")

    #Construim noul nume pt fiecare fisier inlocuind variabilele din sablon
    for i, f in enumerate(fisiere, 1):
        nume, ext = os.path.splitext(f)  # Separam numele de extensie
        nou = sablon.replace("{index}", str(i).zfill(3)).replace("{data}", data)
        nou = nou.replace("{extensie}", ext[1:]).replace("{nume}", nume)
        mapare[f] = nou
        print(f"  {f}  ->  {nou}")

    #confirmare
    if input("\nConfirm? (da/nu): ").strip().lower() not in ("da", "d"):
        print("Anulat.")
        return

    # Redenumire in 2 pasi (cu prefix temporar __t__) pt a evita conflicte de nume
    for v in mapare: os.rename(os.path.join(director, v), os.path.join(director, "__t__" + v))
    for v, n in mapare.items(): os.rename(os.path.join(director, "__t__" + v), os.path.join(director, n))

    # Salvam maparea in .undo.json pentru a putea restaura ulterior
    with open(os.path.join(director, UNDO), "w") as f:
        json.dump(mapare, f, indent=4)
    print(f"\n{len(mapare)} fisiere redenumite!")

#undo: restaureaza denumirile originale din .undo.json
def anuleaza(director):
    cale = os.path.join(director, UNDO)
    if not os.path.exists(cale):
        print("Nu are sens undo,acestea sunt denumirile originale!")
        return

    # Citim maparea salvata (nume_vechi -> nume_nou)
    with open(cale) as f:
        mapare = json.load(f)

    print(f"\nRestaurare {len(mapare)} fisier(e):\n")
    for orig, ren in mapare.items(): print(f"  {ren}  ->  {orig}")

    if input("\nConfirmati? (da/nu): ").strip().lower() not in ("da", "d"):
        print("Anulat.")
        return

    # Restauram in 2 pasi (la fel ca la redenumire, cu prefix temporar)
    for o, r in mapare.items(): os.rename(os.path.join(director, r), os.path.join(director, "__t__" + r))
    for o, r in mapare.items(): os.rename(os.path.join(director, "__t__" + r), os.path.join(director, o))

    os.remove(cale)  # Stergem .undo.json dupa restaurare
    print(f"\n{len(mapare)} fisiere restaurate!")

# Argumente  (linia de comanda)
parser = argparse.ArgumentParser(description="Redenumire automata a fisierelor.")
parser.add_argument("-d", "--director", required=True, help="Directorul cu fisierele")
# Grup exclusiv: utilizatorul alege UNA din cele 3 optiuni
grup = parser.add_mutually_exclusive_group(required=True)
grup.add_argument("-s", "--sablon", help='Sablon, ex: "Img_{index}_{data}.{extensie}"')
grup.add_argument("--config", help="Fisier JSON cu sablonul")
grup.add_argument("--undo", action="store_true", help="Anuleaza ultima redenumire")
args = parser.parse_args()

#Logica principala
if not os.path.isdir(args.director):
    print(f"Eroare: '{args.director}' nu e un director valid.")
elif args.undo:
    anuleaza(args.director)
else:
    # Incarcam sablonul din config.json sau din argumentul -s
    if args.config:
        with open(args.config) as f: sablon = json.load(f)["sablon"]
        print(f"Sablon incarcat din: {args.config}")
    else:
        sablon = args.sablon
    redenumeste(args.director, sablon)
