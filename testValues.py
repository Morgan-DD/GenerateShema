#   createur:               Morgan Dussault
#   Date de creation:       27.02.2024
#   
#   But du script:          Le script sert à tester les valeurs du fichier et si elles ne respectent pas les règle alors cela retourne False sinon ça retourne True
#   
#   notes supp:             compatible sur windows(10) et ubuntu(22.04.4 LTS) pour l'instant
#   version:                version 1.0    
import os
import glob
import sys
import re

if(len(sys.argv) > 1):
    debug = sys.argv[1]

    if(debug.lower() == "-debug"):
        displayDebug = True
else:
    displayDebug = False

# méthode servant à nettoyer une string de ses caractère tel que ["] et [']
#string = une string
def CleanString(string):
    if string[0] == "'" or string[0] == "\"":
        string = string[1:]
    if string[len(string)-1] == "'" or string[len(string)-1] == "\"":
        string = string[:-1]
    return string.replace("\n", "")

def testRegexValue(regex, value):
    return bool(re.match(regex, value))

def printTextOnABox(text):
    length = len(str(text)) +2
    toPrint = ["","│ " + str(text) + " │", ""]
    position = True
    for a in range(0,2):
        for i in range(0,length):
            if(position):
                if i == 0:
                    toPrint[0] = toPrint[0] + "┌"
                toPrint[0] = toPrint[0] + "─"
                if i == length-1:
                    toPrint[0] = toPrint[0] + "┐"
            else:
                if i == 0:
                    toPrint[2] = toPrint[2] + "└"
                toPrint[2] = toPrint[2] + "─"
                if i == length-1:
                    toPrint[2] = toPrint[2] + "┘"
        position = False
        i = 0
    for line in toPrint:
        print(line)
    
# liste des clé et le regex que leurs valeurs doivent respecter
checkValueArray = [["daysuse",r"^[0-9]{1,2}$"],
                   ["project_name",r"^[A-Za-z0-9-.-.]{1,15}$"],
                   ["srv_name",r"^[A-Za-z0-9-.-.]{1,15}$"],
                   ["cli_name",r"^[A-Za-z0-9-.-.]{1,15}$"],
                   ["srvappl_name",r"^[A-Za-z0-9-.-.]{1,15}$"],
                   ["bridge_netid",r"(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){2}"],
                   ["domain_name",r"^((?!-))(xn--)?[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,1}\.(xn--)?([a-z0-9\-]{1,61}|[a-z0-9-]{1,30}\.[a-z]{2,})$"],
                   ["domain_admin_password",r"^.{1,20}$"],
                   ["recovery_password",r"^.{1,20}$"],
                   ["rt_name",r"^[A-Za-z0-9-.-.]{1,15}$"],
                   ["upn",r"^[A-Za-z0-9-.-.]{1,15}$"],
                   ["firstname",r"^.{1,15}$"],
                   ["surname",r"^.{1,15}$"],
                   ["display_name",r"^.{1,20}$"],
                   ["user_password",r"^.{1,20}$"],
                   ["email",r".*@[a-z0-9.-]*"],
                   ["bridge_id",r"^[0-9]{1,2}$"],
                   ["wan_ip",r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$"],]

# on recherche si il y a un fichier .yml dans le meme repertoire que le script et on récupère son nom
script_folder_path = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(script_folder_path)
my_files = glob.glob('*.yml')

# on test si il y a un fichier .yml dans le repertoire
if(len(my_files) <= 0):
    # si non on affiche un message d'erreur
    print("veuilliez ajouter un fichier .yml à coté du script")
else:
    #si oui on commence le script

    # tableau contenant la liste des donée erronées
    errorArray = []
    #tableau contenant la liste des valeur(array[1]) et de leur clé(array[0])
    keyValueArray = []
    # on recupère le contenu du fichier .yml qu'on a trouvé
    fileContent = open(my_files[0]).read()
    # on edit le contenu du fichier pour en faire un tableau et que les donées soient lisibles et utilisables
    fileContent = fileContent.split("\n")
    # on passe par chaque case du tableau
    for line in fileContent:
        # si la case est pas vide (ligne vide ou fausse)
        if((line.split('#'))[0] != ""):
            # on edit notre clé et notre valeur pour les rendre fonctionelles
            lineValue = ((line.split('#'))[0].split(':'))[1].lstrip().rstrip()
            lineKey = ((line.split('#'))[0].split(':'))[0].lstrip().rstrip()
            # on "nettoye notre valeur"
            lineValue = CleanString(lineValue)
            # on met notre clé et notre valeur dans un tableau temporaire
            KeyValueArrayTemp = [lineKey, lineValue]
            # on ajoute ce tableau temporaire à notre tableau principal
            keyValueArray.append(KeyValueArrayTemp)
        del line

    # on passe dans le tableau crée juste en dessu
    for i in range(len(keyValueArray)):
        for regex in checkValueArray:
            # on regarde si notre valeur respecte le regex
            if regex[0] == keyValueArray[i][0] and keyValueArray[i][1] != False:
                testRegex = testRegexValue(regex[1], keyValueArray[i][1])
                testRegex = not testRegex
                # si c'est pas le cas on l'ajoute à un tableau des erreurs
                if (testRegex):
                    errorArray.append(keyValueArray[i])

    if(len(errorArray) > 0):
        if(displayDebug):
            printTextOnABox("resultat: "+ str(False))
        else:
            print(False)
    else:
        print(True)
    if(displayDebug):
        for error in errorArray:
            printTextOnABox("paramètre erroné: " + str(error[0]))
            printTextOnABox("valeur: " + str(error[1]))
