#   createur:               Morgan Dussault
#   Date de creation:       09.02.2024
#   
#   But du script:          Le script sert à créer un shema reseau graçe à des donnée vennant d'un fichier yml et à verifier si les données du fichier sont justes et tout ça sur un serveur ubuntu
#   
#   notes supp:             compatible sur windows(10) et ubuntu(22.04.4 LTS) pour l'instant
#   version:                version 1.0    
import shutil
import platform
import os
import glob
import sys
import re

# méthode servant à nettoyer une string de ses caractère tel que ["] et [']
#string = une string
def CleanString(string):
    if string[0] == "'" or string[0] == "\"":
        string = string[1:]
    if string[len(string)-1] == "'" or string[len(string)-1] == "\"":
        string = string[:-1]
    return string.replace("\n", "")

# sert à retrouver une valeur(numerique de 3 char de long ou moin) dans une balise xml ex:
#       myString = "<mxGeometry width="50" height="50" relative="1" as="geometry">"
#       findValueOnElement(myString, "width")
#       resultat = 50
#element = une string
#valueType = width, relative, geometry(par rapport à l'exemple)
def findValueOnElement(element, valueType):
    if(valueType[-1] != "\""):
        valueType = valueType + "=\""
    localisationString = element.find(valueType)
    return element[(localisationString+len(valueType)):(localisationString+len(valueType)+3)]

#methode qui sert à mettre en forme 2 valeur (principalement utilisée pour le debogage)
def arrangeVariable(var1,var2):
    print("     [" + var1 + " | " + var2 + "]")

# methode qui ecrit le contenu d'un tableau proprement
#array = un tableau
def printArray(array):
    for value in array:
        if(type(value) is array):
            arrangeVariable(value[0], value[1])
    displaySeparation()

# methode qui test un regex et retourne le resultat
#regex = une string contenant un regex ex: string = r"[A-z]{2}[0-9]{2}"
#value = la valeur qui est testée, une string
#ex: testRegexValue(r"[A-z]", "Adasvdhk") = true
def testRegexValue(regex, value):
    return bool(re.match(regex, value))

# methode qui ecrit une separation pour un meilleur visuel
def displaySeparation():
    print("•-------------------------------------------------------------------------------•")

# methode qui sert à rediriger une erreur vers ça methode pour etre affichée
#id = id de la ligne (case 0)
#value = valeur de la ligne (case 1)
def matchingError(id, value):
    # affiche la valeure qui est fausse
    print ("votre entée[" + value + "]\n")
    # liste des erreurs pour chaque valeur (clé, message, exemple)
    errorMessagesList = [["srv_name","Le Nom de votre serveur n'est pas juste, il doit etre comme ceci:","AZA-FC, ashabjhca04-DC, L89-DC,  aaa-ad, test-po"],
                        ["cli_name","Le Nom de votre client n'est pas juste, il doit etre comme ceci:","AZA-FCClient, ashabjhca04-Client, L89-aa,  lala99-C, test-Cli1"],
                        ["bridge_name","Le Nom de votre pont n'est pas juste, il doit etre comme ceci:","Bridge41, Bridge12, aaaa01,  b1, bridge9"],
                        ["bridge_comment","Le commentaire de votre pont n'est pas juste, il doit etre comme ceci:","This is a bridge, lanlanla, 007,  lanAlone, lan12345"],
                        ["bridge_netid","Le netid de votre pont n'est pas juste, il doit etre comme ceci:","167.19.1, 199.0.1, 254.244.245,  1.1.1, 8.8.8"],
                        ["dc_hostname","Le Nom de votre DC n'est pas juste, il doit etre comme ceci:","DC02, DC1000000000000, dc302,  dcD1, dc489c"],
                        ["domain_name","Le Nom de votre domaine n'est pas juste, il doit etre comme ceci:","domain.local, domain.local, google.com,  mydomain1.a, a.a"],
                        ["rt_name","Le Nom de votre routeur n'est pas juste, il doit etre comme ceci:","VT-C003-RT4, RV-b003-rt04, la-p100t-RT5,  BA-B100C-RT24, VS-A103-RT90"],
                        ["upn","Le Nom de votre utilisateur UPN n'est pas juste, il doit etre comme ceci:","ted, IAmTheUser, USERNAmeCool3,  upnUserName, 1-user-2"],
                        ["firstname","Le Nom n'est pas juste, il doit etre comme ceci:","HelloWorld, Rochat, Skywawllker,  nom, thatsAName"],
                        ["surname","Le Prenom n'est pas juste, il doit etre comme ceci:","Marcel, JhonDoe, HelloWorld,  prenom, thatsASurname"],
                        ["display_name","Le Nom affiché n'est pas juste, il doit etre comme ceci:","Mr. Ted Johns, TheGuy, User4,  FriendlyBear, ProxMoxLover"],
                        ["email","L'adresse mail n'est pas juste, il doit etre comme ceci:","Marcel.Rochat@eduvaud.ch, a.a@a.com, Me.cool@outlook.com,  user@VAR.tv, thomas.pereau@army.org"],]
    # recherche le message d'erreur vis à vis de l'id
    errorMessage = getValueOnFileContent(id, errorMessagesList)
    # écrit le message d'erreur et les exemple
    print(errorMessage[1])
    print(errorMessage[2])
    # affiche une ligne de séparartion pour une meilleure lecture
    displaySeparation()
    
# methode qui permet de retrouver une valeur si on a ça clé (value[0] = clé, value[1] = valeur,)
#valueId = id de la ligne (case 0)
#value = valeur de la ligne (case 1)
def getValueOnFileContent(valueId, values):
    for value in values:
        if(value[0] == valueId):
            return value

# methode qui remplace dans le patern des formes du schema les valeur temporaires par les valeurs finale recupérées dans le fichier .yml et retourne le patern
#component = patern
#name = nom de la forme
#x = position x de la forme
#y = position y de la forme
#id = id de la forme
def replaceDataOnComponent(component, name, x, y, id):
    component = component.replace("$name", str(name))
    component = component.replace("$x", str(x))
    component = component.replace("$y", str(y))
    component = component.replace("$id", str(id))
    return component

# methode qui remplace dans le paterne pour le carré avec toutes les informations les valeur temporaires par les valeurs finale recupérées dans le fichier .yml et retourne la string
#component = patern
#id = id de la forme
#user = upn
#name = nom de l'utilisateur
#firstName = prenom de l'utilisateur
#displayName = nom affiché de l'utilisateur
#email = email
#y = position y de la forme
def replaceDataOnSquare(component, id, user, name, firstName, displayName,email, y):
    component = component.replace("$id", str(id))
    component = component.replace("$user", str(user))
    component = component.replace("$name", str(name))
    component = component.replace("$firstName", str(firstName))
    component = component.replace("$displayName", str(displayName))
    component = component.replace("$email", str(email))
    component = component.replace("$y", str(y))
    return component

# methode qui crée un lien entre 2 composants
def createLink(id, x, y, width, height, margin, linkBlock, linkid):
    match id:
        case "srv_name":#si c'est un serveur -> trame reseau
            startX = x + (width/2)
            startY = y + height - 10
            finalX = startX
            finalY = y + height + margin + 10
        case "cli_name":#si c'est un clien -> trame reseau
            startX = x + (width/2)
            startY = y + height - 10
            finalX = startX
            finalY = y + height + margin + 10
        case "rt_name":#si c'est un routeur -> trame reseau
            startX = x + (width/2)
            startY = y +1
            finalX = startX
            finalY = y- margin -1
        case "firewall":#si c'est un firewall -> routeur
            startX = x + (width/2)
            startY = y +1
            finalX = startX
            finalY = y- margin -1
        case "wan":#si c'est le wan -> firewall
            startX = x + (width/2)
            startY = y + 10
            finalX = startX
            finalY = y- margin -1
            linkid="CPNV"
    linkBlock = linkBlock.replace("$id", str(linkid))#id de la liaison
    linkBlock = linkBlock.replace("$xStart", str(startX))#id du début de la liaison(x) 
    linkBlock = linkBlock.replace("$yStart", str(startY))#id du début de la liaison(y)
    linkBlock = linkBlock.replace("$xEnd", str(finalX))#id de la fin de la liaison(x) 
    linkBlock = linkBlock.replace("$yEnd", str(finalY))#id de la fin de la liaison(y)
    return linkBlock

# methode qui génére le shema reseau graçe aux données récupérée et transmises
#values = valeurs des forme et leur id
#x = position x de la forme
#y = position y de la forme
#id = id de la forme
#baseFileValue = paterne de base dans lequel on vien rajouter les formes
def shemaGenerate(values, x, y, id, baseFileValue):

    # taille du schema
    height = 438
    width = 600
    marginTop = 15
    #marge entre les formes
    margin = 50

    #taille des differents composants
    serverSize = [94,94]
    clientSize = [67,91]
    routerSize = [70,70]
    firewallSize = [72,64]
    wanSize = [118,79]
    trameSize = [520,20]

    #ici on récupère le contenu d'un fichier qui contient les paternes pour les différents composants du schema
    coponents = open(coponentFilePath).read()
    # separe par composant
    coponents = coponents.split("|")

    # string contenant les liens entre les formes
    linksList = ""
    # contient une fois le patern des liens sans valeurs
    linkBlock = (coponents[-1].split("!"))[1]
    # patern de toutes les composants du schema avec leurs valeurs
    shemaContent = ""
    for coponent in coponents:
        #mise en forme des "composant" pour les traiter apres
        coponent = (coponent.split("!"))
        coponent[0] = coponent[0].replace("\n", "")
        # test pour savoir à quel composant on à a faire pour le traiter corectement
        match coponent[0]:
            # si c'est le serveur
            case "server":
                # on le met en haut à gauche
                x = ((width - serverSize[0])/3)*2
                y = marginTop
                # on modifie le paterne en ajoutant nos donées
                shemaContent = "\n".join([shemaContent + replaceDataOnComponent(coponent[1], (getValueOnFileContent("srv_name", values))[1], x, y, id)])
                # on augmente l'id pour eviter des bugs
                id = id+1
                # on crée la liaison qui relie le serveur à la trame
                linksList = linksList+ createLink("srv_name", x, y,serverSize[0], serverSize[1], margin, linkBlock, id)
                # on augmente l'id pour eviter des bugs
                id = id+1
            # si c'est le client
            case "client":
                # on le met en haut à gauche
                x = (width - clientSize[0])/3
                y = marginTop
                # on modifie le paterne en ajoutant nos donées
                shemaContent = "\n".join([shemaContent, replaceDataOnComponent(coponent[1], (getValueOnFileContent("cli_name", values))[1], x, y, id)])
                # on augmente l'id pour eviter des bugs
                id = id+1
                # on crée la liaison qui relie le client à la trame
                linksList = linksList+ createLink("cli_name", x, y,clientSize[0], clientSize[1], margin, linkBlock, id)
                # on augmente l'id pour eviter des bugs
                id = id+1
            # si c'est la trame
            case "trame":
                # on le met sous les clients et les serveurs
                x = (width - trameSize[0])/2
                y = (serverSize[1] + marginTop + margin)
                text = str((getValueOnFileContent("bridge_name", values))[1]) + " | " + str((getValueOnFileContent("bridge_comment", values))[1]) + " | "  + str((getValueOnFileContent("bridge_netid", values))[1]) + ".0/24"
                # on modifie le paterne en ajoutant nos donées
                shemaContent = shemaContent + replaceDataOnComponent(coponent[1], text , x, y, id)
                # on augmente l'id pour eviter des bugs
                id = id+1
            # si c'est le routeur
            case "router":
                # on le met sous la trame
                x = (width - routerSize[0])/2
                y = (serverSize[1] + trameSize[1] + marginTop + margin*2)
                # on modifie le paterne en ajoutant nos donées
                shemaContent = shemaContent + replaceDataOnComponent(coponent[1], (getValueOnFileContent("rt_name", values))[1], x, y, id)
                # on augmente l'id pour eviter des bugs
                id = id+1
                linksList = linksList+ createLink("rt_name", x, y,routerSize[0], routerSize[1], margin, linkBlock, id)
                # on augmente l'id pour eviter des bugs
                id = id+1
            # si c'est le firewall
            case "firewall":
                """
                # on le met sous le router
                x = (width - firewallSize[0])/2
                y = (serverSize[1] + trameSize[1] + routerSize[1] + marginTop + margin*3)
                # on modifie le paterne en ajoutant nos donées
                shemaContent = shemaContent + replaceDataOnComponent(coponent[1], "", x, y, id)
                # on augmente l'id pour eviter des bugs
                id = id+1
                linksList = linksList+ createLink("firewall", x, y,firewallSize[0], firewallSize[1], margin, linkBlock, id)
                # on augmente l'id pour eviter des bugs
                id = id+1
                """
            # si c'est le wan
            case "wan":
                # on le met sous le firewall
                x = (width - wanSize[0])/2
                y = (serverSize[1] + trameSize[1] + routerSize[1] + marginTop + margin*3)
                # on modifie le paterne en ajoutant nos donées
                shemaContent = shemaContent + replaceDataOnComponent(coponent[1],"", x, y, id)
                # on augmente l'id pour eviter des bugs
                id = id+1
                linksList = linksList+ createLink("wan", x, y,wanSize[0], wanSize[1], margin, linkBlock, id)
                # on augmente l'id pour eviter des bugs
                id = id+1
            # si c'est le tableau de donée
            case "dataArray":
                # patern
                square = coponent[1]
                # on recupère la hauteur du cube pour pouvoir le placer tout en bas à droite
                stringToFind = 'height'
                #hauteur du carré
                squareHeight = findValueOnElement(square,stringToFind)
                # utilisateur upn
                user = (getValueOnFileContent("upn", values))[1]
                # nom de famille de l'utilisateur
                name = (getValueOnFileContent("surname", values))[1]
                # prenom de l'utilisateur
                firstname = (getValueOnFileContent("firstname", values))[1]
                # nom affichée de l'utilisateur
                displayName = (getValueOnFileContent("display_name", values))[1]
                # email
                email = (getValueOnFileContent("email", values))[1]
                # position y du carré
                squareY = int(height) - int(squareHeight)
                # on modifie le paterne en ajoutant nos donées
                square = replaceDataOnSquare(square, id,user,name,firstname,displayName,email,squareY)
                # on ajoute notre carré au schema
                shemaContent = shemaContent + square
                # on augmente l'id pour eviter des bugs
                id = id+1

    # on ajoute notre liste de lien au shema mais au début car plus c'est au debut plus c'est en dessous donc les liens seront en dessous des icones
    shemaContent = linksList + shemaContent
    # on ajoute nos formes au fichier de base
    baseFileValue = baseFileValue.replace("$REPLACEME", shemaContent)
    # on change la hauteur du shema
    baseFileValue = baseFileValue.replace("$height", str(height))
    # on change la largeur du shema
    baseFileValue = baseFileValue.replace("$width", str(width))
    # on ouvre le fichier de destination (sur le bureau) aprecu.drawio
    file = open(descktopPath, "w")
    # on ecris dans notre fichier le contenu
    file.write(baseFileValue)
    # on ferme le fichier
    file.close

#position x actuelle formes dans sur le schema
actualX = 25
#position y actuelle des formes dans sur le schema
actualY = 25
#id actuelle des formes dans sur le schema
actualId = 0

# liste des clé et le regex que leurs valeurs doivent respecter
checkValueArray = [["srv_name",r"^.{1,15}$"],
                   ["cli_name",r".{1,15}"],
                   ["bridge_name",r"^.{1,8}$"],
                   ["bridge_comment",r"^.{1,8}$"],
                   ["bridge_netid",r"(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){2}"],
                   ["dc_hostname",r"^.{1,15}$"],
                   ["domain_name",r"^((?!-))(xn--)?[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,1}\.(xn--)?([a-z0-9\-]{1,61}|[a-z0-9-]{1,30}\.[a-z]{2,})$"],
                   ["domain_admin_password",r"^.{1,20}$"],
                   ["recovery_password",r"^.{1,20}$"],
                   ["rt_name",r"[A-z]{2}-[A-z][0-9]{3}([A-z]?)-[A-z]{2}[0-9]{2}"],
                   ["upn",r"^.{1,15}$"],
                   ["firstname",r"^.{1,15}$"],
                   ["surname",r"^.{1,15}$"],
                   ["display_name",r"^.{1,20}$"],
                   ["user_password",r"^.{1,20}$"],
                   ["email",r".*@[a-z0-9.-]*"],]

# nom du fichier drawio final 
destination = "aprecu.drawio"

# test pour savoir si on est sur windows ou pas
index = (platform.system().lower()).find("windows")

pathFormat = "/"

# on definit le chemin du bureau et le separateur dans le chemin entre winodws et linux
if index >= 0:
    pathFormat = "\\"
    descktopPath = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') + pathFormat + destination
else:
    descktopPath = os.path.join(os.path.join(os.path.expanduser('~')), '') + "Bureau/" + destination


script_folder_path = os.path.dirname(os.path.abspath(sys.argv[0]))

#chemin du fichier qui contient la base du schema
baseFilepath = script_folder_path + pathFormat + "component" + pathFormat + "base.txt"
#chemin du fichier qui contient les différents paterns
coponentFilePath = script_folder_path + pathFormat + "component" + pathFormat + "block.txt"

# copie du fichier de base sur le bureau
shutil.copyfile(baseFilepath, descktopPath)

# on copie le contenu de se fichier
baseFileValue = open(descktopPath).read()

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
            if regex[0] == keyValueArray[i][0]:
                testRegex = testRegexValue(regex[1], keyValueArray[i][1])
                testRegex = not testRegex
                # si c'est pas le cas on l'ajoute à un tableau des erreurs
                if (testRegex):
                    errorArray.append(keyValueArray[i])

    # on passe dans le tableau des erreurs crée juste en dessu
    for error in errorArray:
        # on affiche le message d'erreur lié à l'erreur
        matchingError(error[0], error[1])

    # ici on genère le shema du reseau
    shemaGenerate(keyValueArray, actualX, actualY, actualId, baseFileValue)