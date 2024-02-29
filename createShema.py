#   createur:               Morgan Dussault
#   Date de creation:       09.02.2024
#   
#   But du script:          Le script sert à créer un shema reseau graçe à des donnée vennant d'un fichier yml et à verifier si les données du fichier sont justes et tout ça sur un serveur ubuntu
#   
#   notes supp:             compatible sur windows(10) et ubuntu(22.04.4 LTS) pour l'instant
#   version:                version 1.1  
import shutil
import platform
import os
import glob
import sys
import re

def DisplayList(matrix, id, blockList, idLongerItem, baseFileValue, idsBigestHeight, idsBigestWidth):

    marginSide = 25
    midMargin = 50
    
    itemTotalWith = 0

    matrixNewValue = []

    for singleBlock in matrix[idLongerItem]:
        itemTotalWith=itemTotalWith+GetSize(singleBlock)[1]
        
    tempheight=0
    totalWith = []
    tempwidth = 0
    lastX = 0
    lastY = 0
    arrayX = 0
    arrayY = 0
    tempLineNewValue = []
    idLine = 0
    idItem =0
    for line in matrix: 

        lastX = 0
        if(lastY > 0):
            y = lastY + midMargin
        else:
            y = lastY + marginSide

        for singleBlock in line:
            if(lastX > 0):
                x = lastX
            else:
                x = lastX

            tempwidth = tempwidth + (GetSize(singleBlock))[0]
            formHeight = GetSize(singleBlock)[1]
            
            if(formHeight > tempheight):
                tempheight = GetSize(singleBlock)[1]
            lastX = x + GetSize(singleBlock)[0]
            lastY = y + GetSize(singleBlock)[1]
            print("["+str(idItem)+ "]")
            print("x:" + str(x))
            print("Bigest width: " + str(((GetSize(matrix[idsBigestWidth[0]][idsBigestWidth[1]])[0]))))
            print("item width: " + str(GetSize(singleBlock)[0]))
            print("difference width: " + str((((GetSize(matrix[idsBigestWidth[0]][idsBigestWidth[1]])[0]))-GetSize(singleBlock)[0])/2))
            print("x + difference width: " + str((x + ((((GetSize(matrix[idsBigestWidth[0]][idsBigestWidth[1]])[0]))-GetSize(singleBlock)[0])/2))))
            print("-----")
            #y=y + ((((GetSize(matrix[idsBigestHeight[0]][idsBigestHeight[1]])[1]))-GetSize(singleBlock)[1])/2)
            tempLineNewValue.append([singleBlock, idItem, x, y, idLine])
            #tempLineNewValue.append([singleBlock, idItem, (x + ((((GetSize(matrix[idsBigestWidth[0]][idsBigestWidth[1]])[0]))-GetSize(singleBlock)[0])/2)), (y + ((((GetSize(matrix[idsBigestHeight[0]][idsBigestHeight[1]])[1]))-GetSize(singleBlock)[1])/2)), idLine])
            idItem=idItem+1
            arrayX = arrayX +1

        arrayY = arrayY +1
        arrayX = 0
        
        matrixNewValue=matrixNewValue+tempLineNewValue
        tempLineNewValue.clear()
        idLine=idLine+1

        height=tempheight
        totalWith.append(tempwidth)
        tempwidth = 0

    width = itemTotalWith + (len(matrix[idLongerItem])-1)*midMargin + marginSide*2
    height = height + (len(blockList)-1)*midMargin + marginSide*2

    idItem = 0
    countItemOnLine=1
    for item in matrixNewValue:
            if(item[0] == "trame"):
                matrixNewValue[idItem][2] = item[2] + int((width - (width - 2*marginSide)) / (len(matrix[item[4]])+1))
            else:  
                spaceValue = int((width - totalWith[item[4]]) / (nbOnLine(matrixNewValue,item[4])+1))
                matrixNewValue[idItem][2] = item[2] + spaceValue*countItemOnLine

            if(idItem < len(matrixNewValue) -1):
                if(matrixNewValue[idItem][4] == matrixNewValue[idItem+1][4]):
                    countItemOnLine=countItemOnLine+1
                else:
                    countItemOnLine=1
            idItem=idItem+1
    nbOnLine(matrixNewValue, 0)
    FinalBlock = ""
    for item in matrixNewValue:
        if(item[0] == "trame"):
            FinalBlock = FinalBlock + replaceDataOnTrame(getValueOnFileContent(item[0], blockList)[1], "trame", item[2], item[3], width - 2*marginSide,id)
        else:
            FinalBlock = FinalBlock + replaceDataOnComponent(getValueOnFileContent(item[0], blockList)[1], item[1], item[2], item[3],id)
        id=id+1

    linkList = joinEverything(blockList[-1], matrixNewValue, idLongerItem, id, midMargin)

    # on ajoute notre liste de lien au shema mais au début car plus c'est au debut plus c'est en dessous donc les liens seront en dessous des icones
    shemaContent = linkList + FinalBlock
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

def joinEverything(linkBlock, matrix, idLongerItem, id, margin):
    idLine = 0
    idItem = 0
    linksList =""
    itemsUnder = []
    itemsUpper = []
    linked = [False, False]
    for item in matrix:
        idLine = item[4]
        if(idLine < len(matrix)-1 and idLine >= 0):
            itemsUnder = itemsUnder + getItemByLine(matrix, item[4]+1)
            itemsUpper = itemsUpper + getItemByLine(matrix, item[4]-1)
            for itemUnder in itemsUnder:
                if(matrix[itemUnder][0] == "trame" and item[0] != "trame" and not linked[0]):
                        if(canConnect(item[0], matrix[itemUnder][0])):
                            linksList=linksList+str(createLinkToTrame(item[0],item[2],item[3], linkBlock[1], id, margin, True, matrix[itemUnder][3]))
                            linked[0] = True
                            id=id+1
                elif(item[0] != "trame" and item[0] != "dataArray"):
                        if(canConnect(item[0], matrix[itemUnder][0])):
                            linksList=linksList+str(createLink(item[0],item[2],item[3],GetSize(item[0])[0], GetSize(item[0])[1], linkBlock[1], id, matrix[itemUnder][2], matrix[itemUnder][3], matrix[itemUnder][0], True))
                            id=id+1                    
                            linked[0] = True
            for itemUpper in itemsUpper:
                if(matrix[itemUpper][0] == "trame" and item[0] != "trame" and not linked[1]):
                        if(canConnect(item[0], matrix[itemUpper][0])):
                            linksList=linksList+str(createLinkToTrame(item[0],item[2],item[3], linkBlock[1], id, margin, False, matrix[itemUpper][3]))
                            linked[1] = True
                            id=id+1
        linked = [False, False]      
        idItem=idItem+1
        itemsUnder.clear()
        itemsUpper.clear()
    return linksList


def getItemByLine(itemList, line):
    ids=[]
    idItemOnList = 0
    for item in itemList:
        if(item[4] == line and item[4] != ""):
            ids.append(idItemOnList)
        idItemOnList=idItemOnList+1
    return ids

def createLinkToTrame(id, x, y, linkBlock, linkid,margin, direction, trameY):
    if(direction):
        startX=x + (GetSize(id)[0])/2
        startY=y+ GetSize(id)[1] - (GetSize(id)[1]/10)
        finalX= startX
        finalY= trameY + (GetSize(id)[1]/5)
    else:
        startX=x + (GetSize(id)[0])/2
        startY=y+ + (GetSize(id)[1]/10)
        finalX= startX
        finalY= trameY + GetSize("trame")[1] - (GetSize(id)[1]/5)
    linkBlock = linkBlock.replace("$id", str(linkid))#id de la liaison
    linkBlock = linkBlock.replace("$xStart", str(startX))#id du début de la liaison(x) 
    linkBlock = linkBlock.replace("$yStart", str(startY))#id du début de la liaison(y)
    linkBlock = linkBlock.replace("$xEnd", str(finalX))#id de la fin de la liaison(x) 
    linkBlock = linkBlock.replace("$yEnd", str(finalY))#id de la fin de la liaison(y)

    return linkBlock



def createLink(id, x, y, width, height, linkBlock, linkid, finalX, finalY, finalId, direction):
    startX = x + (GetSize(id)[0])/2
    finalX = finalX + (GetSize(finalId)[0])/2
    finalY = finalY + (GetSize(id)[1])/8
    startY = y + GetSize(id)[1] - (GetSize(id)[1])/8
    linkBlock = linkBlock.replace("$id", str(linkid))#id de la liaison
    linkBlock = linkBlock.replace("$xStart", str(startX))#id du début de la liaison(x) 
    linkBlock = linkBlock.replace("$yStart", str(startY))#id du début de la liaison(y)
    linkBlock = linkBlock.replace("$xEnd", str(finalX))#id de la fin de la liaison(x) 
    linkBlock = linkBlock.replace("$yEnd", str(finalY))#id de la fin de la liaison(x) 

    return linkBlock

def canConnect(idStart, idFinal):
    verification = [["server",["trame","switch","router","firewall","wan","server","client"]],
                    ["client",["trame","switch","router","firewall","wan","server","client"]],
                    ["router",["trame","switch","router","firewall","wan","server","client"]],
                    ["firewall",["trame","switch","router","firewall","wan","server","client"]],
                    ["switch",["trame","switch","router","firewall","wan","server","client"]],
                    ["wan",["trame","switch","router","firewall","wan","server","client"]],]
    for idStartMatch in verification:
        if(idStartMatch[0] == idStart):
            for idFinalMatch in idStartMatch[1]:
                if (idFinalMatch == idFinal):
                    return True
    return False
def GetSize(id):
    serverSize = [94,94]
    clientSize = [67,91]
    switchSize = [59,59]
    routerSize = [70,70]
    firewallSize = [72,64]
    wanSize = [118,79]
    trameSize = [520,20]
    match id:
            # si c'est le serveur
            case "server":
                return serverSize
            # si c'est le client
            case "client":
                return clientSize 
            # si c'est la trame
            case "trame":
                return trameSize
            # si c'est le routeur
            case "router":
                return routerSize
            # si c'est le switch
            case "switch":
                return switchSize
            # si c'est le firewall
            case "firewall":
                return firewallSize
            # si c'est le wan
            case "wan":
               return wanSize
            case _:
                return 0

def nbOnLine(array, lineId):
    counter = 0
    for value in array:
        if(value[4] == lineId):
            counter=counter+1
    return counter

def getValueOnFileContent(valueId, values):
    for value in values:
        if(value[0] == valueId):
            return value
        
def replaceDataOnComponent(component, name, x, y, id):
    component = component.replace("$name", str(name))
    component = component.replace("$x", str(x))
    component = component.replace("$y", str(y))
    component = component.replace("$id", str(id))
    return component

def replaceDataOnTrame(component, name, x, y, witdh, id):
    component = component.replace("$name", str(name))
    component = component.replace("$x", str(x))
    component = component.replace("$y", str(y))
    component = component.replace("$width", str(witdh))
    component = component.replace("$id", str(id))
    return component

def checkLineId(line, id):
    if(id < len(line)):
        return line[id][0]

def isData(keyValueArray, idItemKey):
    itemList = ["trame","switch","router","firewall","wan","server","client"]
    if(idItemKey < len(keyValueArray)):
        for item in itemList:
            if(item == matchingDataWithId(keyValueArray[idItemKey][0])):
                return False
    return True

    
def isATrame(name):
    if(name == "trame" or name.startswith("bridge")):
        return True
    else:
        return False

def matchingDataWithId(data):
    if(data.startswith("bridge_")):
        return "trame"
    match data:
            # si c'est le serveur
            case "srv_name":
                return "server"
            # si c'est le client
            case "cli_name":
                return "client" 
            # si c'est le routeur
            case "rt_name":
                return "router"
            # si c'est le switch
            case "sw_name":
                return "switch"
            # si c'est le firewall
            case "firewall":
                return "firewall"
            # si c'est le wan
            case "wan":
               return "wan"
            case _:
                return ""

def arrangeVariable(var1,var2):
    print("     [" + var1 + " | " + var2 + "]")

def isLinkable(data):
    if(not isATrame(data) or data != "dataArray"):
        return True
    else:
        return False

def displaySeparation():
    print("•-------------------------------------------------------------------------------•")

def printArray(array):
    for value in array:
        if(type(value) is array):
            arrangeVariable(value[0], value[1])
        else:
            print(value)
    displaySeparation()

def CleanString(string):
    if string[0] == "'" or string[0] == "\"":
        string = string[1:]
    if string[len(string)-1] == "'" or string[len(string)-1] == "\"":
        string = string[:-1]
    return string.replace("\n", "")

def testRegexValue(regex, value):
    return bool(re.match(regex, value))

def matchingError(id, value):
    # affiche la valeure qui est fausse
    print ("votre entée[" + value + "]")
    # liste des erreurs pour chaque valeur (clé, message, exemple)
    errorMessagesList = [["srv_name","Le Nom de votre serveur n'est pas juste, il doit etre comme ceci:","Test10-DC, ashabjhca04-DC, L89-DC,  lala99-DC, ProxMox04-DC"],
                        ["cli_name","Le Nom de votre client n'est pas juste, il doit etre comme ceci:","Test10-Cli1, ashabjhca04-Cli1, L89-Cli1,  lala99-Cli1, ProxMox04-Cli1"],
                        ["bridge_name","Le Nom de votre pont n'est pas juste, il doit etre comme ceci:","vmbr19, Bridge12, aaaa01,  b1, bridge9"],
                        ["bridge_comment","Le commentaire de votre pont n'est pas juste, il doit etre comme ceci:","lanTest9, lanlanla, 007,  lanAlone, lan12345"],
                        ["bridge_netid","Le netid de votre pont n'est pas juste, il doit etre comme ceci:","192.168.10, 199.0.1, 254.244.245,  1.1.1, 8.8.8"],
                        ["dc_hostname","Le Nom de votre DC n'est pas juste, il doit etre comme ceci:","DC10, DC1000000000000, dc302,  dcD1, dc489c"],
                        ["domain_name","Le Nom de votre domaine n'est pas juste, il doit etre comme ceci:","ict123-9.loc, domain.local, google.com,  MonDomaine1.a, a.a"],
                        ["rt_name","Le Nom de votre routeur n'est pas juste, il doit etre comme ceci:","YV-A103-RT01, sc-b003-rt04, la-p100t-rt45,  PA-B100C-RT24, SC-A103-RT90"],
                        ["upn","Le Nom de votre utilisateur UPN n'est pas juste, il doit etre comme ceci:","ted, IAmTheUser, USERNAmeCool3,  upnUserName, 1-user-2"],
                        ["firstname","Le Nom n'est pas juste, il doit etre comme ceci:","HelloWorld, Rochat, Skywawllker,  nom, thatsAName"],
                        ["surname","Le Prenom n'est pas juste, il doit etre comme ceci:","Marcel, JhonDoe, HelloWorld,  prenom, thatsASurname"],
                        ["display_name","Le Nom affiché n'est pas juste, il doit etre comme ceci:","Mr. Ted Johns, TheGuy, User4,  FriendlyBear, ProxMoxLover"],
                        ["email","L'adresse mail n'est pas juste, il doit etre comme ceci:","Marcel.Rochat@eduvaud.ch, a.a@a.com, Me.cool@outlook.com,  user@swiss.tv, thomas.pereau@army.org"],]
    # recherche le message d'erreur vis à vis de l'id
    errorMessage = getValueOnFileContent(id, errorMessagesList)
    # écrit le message d'erreur et les exemple
    print(errorMessage[1])
    print(errorMessage[2])
    # affiche une ligne de séparartion pour une meilleure lecture
    displaySeparation()

destination = "aprecu.drawio"

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
        if(keyValueArray[i][1] != ""):
            for regex in checkValueArray:
                # on regarde si notre valeur respecte le regex
                if regex[0] == keyValueArray[i][0]:
                    testRegex = testRegexValue(regex[1], keyValueArray[i][1])
                    testRegex = not testRegex
                    # si c'est pas le cas on l'ajoute à un tableau des erreurs
                    if (testRegex):
                        errorArray.append(keyValueArray[i])

    matrix = []
    matrixLine =[]
    addToMatrix = False
    idItemKey = 0
    print("longeur keyValueArray: " + str(len(keyValueArray)))
    print("...,...,...,...,...,...,...,...,...,...,...,...,...,...,...")
    for item in keyValueArray:
        print("item id: " + str(idItemKey))
        itemId = matchingDataWithId(item[0])
        if(itemId != ""):
            print(itemId)
            print("linkable: " + str(isLinkable(itemId)))
            if(isLinkable(itemId)):
                matrixLine=matrixLine+([itemId])
            print("next: " + str((checkLineId(keyValueArray, idItemKey+1))))
            print("is trame: " + str(isATrame(checkLineId(keyValueArray, idItemKey+1))))
            print("is last: " + str(idItemKey == len(keyValueArray)))
            print("is data: " + str(isData(keyValueArray, idItemKey+1)))
            if(isATrame(checkLineId(keyValueArray, idItemKey+1)) or idItemKey == len(keyValueArray) or isData(keyValueArray, idItemKey+1)):
                addToMatrix = True
        idItemKey=idItemKey+1
        if(addToMatrix):
            print("ligne: " + str(matrixLine))
            matrix.append(matrixLine)
            addToMatrix = False
            matrixLine=[]
        print("------------------------------------------------------------")
    print("matrix:")
    print(matrix)

    displaySeparation()
    # on passe dans le tableau des erreurs crée juste en dessu
    for error in errorArray:
        # on affiche le message d'erreur lié à l'erreur
        matchingError(error[0], error[1])

coponents = open(coponentFilePath).read()
# separe par composant
coponents = coponents.split("|")

blockList = []

for component in coponents:
    component = component.split("!")
    blockList = blockList + [[component[0].replace("\n", ""), component[1]]]



if(len(matrix) > 0):
    id = 0
    idLongerItem = 0
    idLineBigestWidth = 0
    idItemBigestWidth = 0
    idLineBigestHeight = 0
    idItemBigestHeight = 0
    LongestWith = 0
    lineId = 0
    itemId = 0
    for line in matrix:
        for item in line:
            if(GetSize(matrix[idLineBigestHeight][idItemBigestHeight])[1] < GetSize(item)[1] and item != "trame" and item != "dataArray"):
                idLineBigestHeight = lineId
                idItemBigestHeight = itemId
            if(GetSize(matrix[idLineBigestWidth][idItemBigestWidth])[1] < GetSize(item)[0] and item != "trame" and item != "dataArray"):
                idLineBigestWidth = lineId
                idItemBigestWidth = id
            itemId=itemId+1
        if len(line) > LongestWith:
            LongestWith = len(line)
            idLongerItem = lineId
        lineId=lineId+1
    id = DisplayList(matrix, id, blockList, idLongerItem, baseFileValue, [idLineBigestHeight,idItemBigestHeight], [idLineBigestWidth,idItemBigestWidth])