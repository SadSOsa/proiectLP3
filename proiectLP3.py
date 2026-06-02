import os, json, argparse, datetime

UNDO = ".undo.json"

def redenumeste(director, sablon):
    # protectie in cazul in care exista deja un .undo.json (daca se ruleaza,practic se suprascriu denumirile originale)
    if os.path.exists(os.path.join(director, UNDO)):
        print("ATENTIE!!: Exista deja o redenumire anterioara nesalvata!")
        print("Folositi --undo pentru a restaura fisierele inainte de o noua redenumire.")
        if input("Continuati oricum? (da/nu): ").strip().lower() not in ("da", "d"):
            print("Anulat.Foloseste --undo mai intai.")
            return

    fisiere = sorted(f for f in os.listdir(director)
                     if os.path.isfile(os.path.join(director, f)) and not f.startswith("."))
    if not fisiere:
        print("Nu s-au gasit fisiere.")
        return

    data = datetime.datetime.now().strftime("%Y-%m-%d")
    mapare = {}
    print(f"\nDirector: {os.path.abspath(director)}\nSablon:   {sablon}\n")

    for i, f in enumerate(fisiere, 1):
        nume, ext = os.path.splitext(f)
        nou = sablon.replace("{index}", str(i).zfill(3)).replace("{data}", data)
        nou = nou.replace("{extensie}", ext[1:]).replace("{nume}", nume)
        mapare[f] = nou
        print(f"  {f}  ->  {nou}")

    if input("\nConfirm? (da/nu): ").strip().lower() not in ("da", "d"):
        print("Anulat.")
        return

    for v in mapare: os.rename(os.path.join(director, v), os.path.join(director, "__t__" + v))
    for v, n in mapare.items(): os.rename(os.path.join(director, "__t__" + v), os.path.join(director, n))

    with open(os.path.join(director, UNDO), "w") as f:
        json.dump(mapare, f, indent=4)
    print(f"\n{len(mapare)} fisiere redenumite!")

def anuleaza(director):
    cale = os.path.join(director, UNDO)
    if not os.path.exists(cale):
        print("Nu are sens undo,acestea sunt denumirile originale!")
        return

    with open(cale) as f:
        mapare = json.load(f)

    print(f"\nRestaurare {len(mapare)} fisier(e):\n")
    for orig, ren in mapare.items(): print(f"  {ren}  ->  {orig}")

    if input("\nConfirmati? (da/nu): ").strip().lower() not in ("da", "d"):
        print("Anulat.")
        return

    for o, r in mapare.items(): os.rename(os.path.join(director, r), os.path.join(director, "__t__" + r))
    for o, r in mapare.items(): os.rename(os.path.join(director, "__t__" + r), os.path.join(director, o))

    os.remove(cale)
    print(f"\n{len(mapare)} fisiere restaurate!")

#argumente
parser = argparse.ArgumentParser(description="Redenumire automata a fisierelor.")
parser.add_argument("-d", "--director", required=True, help="Directorul cu fisierele")
grup = parser.add_mutually_exclusive_group(required=True)
grup.add_argument("-s", "--sablon", help='Sablon, ex: "Img_{index}_{data}.{extensie}"')
grup.add_argument("--config", help="Fisier JSON cu sablonul")
grup.add_argument("--undo", action="store_true", help="Anuleaza ultima redenumire")
args = parser.parse_args()

if not os.path.isdir(args.director):
    print(f"Eroare: '{args.director}' nu e un director valid.")
elif args.undo:
    anuleaza(args.director)
else:
    if args.config:
        with open(args.config) as f: sablon = json.load(f)["sablon"]
        print(f"Sablon incarcat din: {args.config}")
    else:
        sablon = args.sablon
    redenumeste(args.director, sablon)
