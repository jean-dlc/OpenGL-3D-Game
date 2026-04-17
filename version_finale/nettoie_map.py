#utilisation ponctuelle de python pour nettoyer le fichier map.json

import json

# Ouvre le fichier map.json et charge les donnée
with open("test_jean5/map.json", "r") as f:
    data = json.load(f)

# On va supprimer les doublons : chaque bloc est converti en tuple pour être mis dans un set
unique_blocks = []
seen = set()
for block in data:
    t = tuple(block)  # On transforme la liste en tuple 
    if t not in seen:
        seen.add(t)
        unique_blocks.append(block)  # On garde le bloc s'il n'est pas déjà vu

# Affiche le nombre de blocs avant et après nettoyage 
print(f"Blocs avant nettoyage : {len(data)}")
print(f"Blocs après nettoyage : {len(unique_blocks)}")

# Réécrit le fichier map.json avec la liste nettoyée
with open("version_finale/map.json", "w") as f:
    json.dump(unique_blocks, f, indent=2)  # On met un peu d'indentation pour que ce soit lisible
