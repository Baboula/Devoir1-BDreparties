import os
from typing import List
import requests
from pathlib import Path
from threading import Thread
import json

#Cette fonction récupère les components de chaque spell
#et les met en forme pour qu'ils prennent la forme d'une liste dans le json
def dispay_components(components):
    all_components = []
    monstr = ""
    for i in components:
        if i == ",":
            all_components.append(monstr.strip().replace("\r", ""))
            monstr = ""
        if i != ",":
            monstr += i
    return all_components

#Cette fonction a pour objectif de récupérer deux informations :
#- Ce sppell est-il un spell de wizard ?
#- Quel est le niveau de ce sort (prend le niveau de wizard) ?
# et les met en forme pour le json
def display_levels(level):
    all_levels = dict()
    levels = level.strip().split(",")
    for level in levels:
        splat = level.strip().split(" ")
        all_levels[splat[0]] = splat[1]

    txt = '    "wizard": '
    wizard = all_levels.get("wizard", 0)
    txt += str(bool(wizard)).lower()

    txt += ',    "level": '
    txt += str(wizard)

    return txt

#Cette fonction est la fonction principale:
#elle se rend sur la page d'un spell et récupère les informations que nous souhaitons intégrées à notre json.
#C'est elle qui appelle les fonctions présentent au dessus
def make_json_spell(spell, list: List):
    #On récupère le code html de la page du sort souhaité
    spell = spell.strip()
    url = 'https://aonprd.com/SpellDisplay.aspx?ItemName=' + spell
    r = requests.get(url)
    truc = r.text

    #On écrit le json
    spell_info = "{\n"

    #Le nom du spell
    spell_info += '    "name": "' + spell + '", \n'

    #Le niveau du spell (appelle "display_level")
    index = truc.find("Level</b>") + 9
    if index <= 9:
        spell_info += '    "level": "0",\n'
    else:
        truc = truc[index:]
        spell_info += display_levels(truc[0:truc.find("<h3")].strip()) + ', \n'

    #Les components du spell (appelle "display_components")
    index = truc.find("Components</b>") + 14
    if index <= 14:
        spell_info += '    "spell_resistance": "no"\n'
    else:
        truc = truc[index:]
        components = truc[0:truc.find("<h3")] + '", \n'
        all_components = dispay_components(components)
        spell_info += '    "components": ['
        for k in range(len(all_components) - 1):
            spell_info += '"' + all_components[k].strip() + '", '
        spell_info += '"' + \
            all_components[len(all_components) - 1].strip() + '],\n'

    #La spell résistance
    index = truc.find("Spell Resistance</b>") + 20
    if index <= 20:
        spell_info += '    "spell_resistance": "no"\n'
    else:
        truc = truc[index:]
        spell_info += '    "spell_resistance": "' + \
            truc[0:truc.find("<h3")].strip() + '"\n'

    spell_info += "},\n"

    list.append(spell_info)

#Récupère le code html de la page contenant tous les noms de spell
url = 'https://aonprd.com/Spells.aspx?Class=All'
r = requests.get(url)
truc = r.text

tab_spell = []

i = 1

#Parcours le html pour obtenir tous les noms de spell
#et stocke tous ces noms dans un tableau
while(i >= 0):
    i = truc.find("SpellDisplay.aspx?ItemName=")
    if i >= 0:
        truc = truc[i + 27:]
        guillemets = truc.find('"')
        tab_spell.append(truc[0: guillemets])

#Le fichier de sortie du json
filename = r"onlinespells2.json"
file_path = Path.cwd().joinpath(filename)

#Afin d'accélerer le processus, on crée des thread pour récupérer plusieurs informations à la fois
all_spells = []
threads = []
n_threads = 512

count = 0
count_f_path = Path.cwd().joinpath("count")

if not Path.exists(count_f_path):
    with open(count_f_path, "x") as count_f:
        count_f.write("0")
else:
    with open(count_f_path) as count_f:
        count = int(count_f.read())

if not file_path.exists():
    with open(file_path, "x") as all_spells_f:
        all_spells_f.write("[\n")

#La main loop qui va (à partir de la liste des noms de spell)
#récupérer leurs informations en se basant sur la fonction "make_json_spell"
for j in range(len(tab_spell)):

    if j < count:
        continue

    print(j)
    if tab_spell[j] != "Status, Greater":

        t = Thread(target=make_json_spell, args=[tab_spell[j], all_spells])
        t.start()
        threads.append(t)
    if len(threads) >= n_threads:
        for t in threads:
            t.join()
            count += 1

        with open(file_path, "a") as all_spells_f:
            all_spells_f.writelines(all_spells)

        with open(count_f_path, "wt") as count_f:
            count_f.write(str(count))

        all_spells = []
        threads = []

with open(file_path, "r") as all_spells_f:
    all_spells = all_spells_f.read()

all_spells = all_spells[:-2] + "\n]"

with open(file_path, "w") as all_spells_f:
    all_spells_f.write(json.dumps(json.loads(all_spells)))

os.remove(count_f_path)
