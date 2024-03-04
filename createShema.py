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

if(len(sys.argv) > 1):
    ymlFilePath = sys.argv[1]
else:
    ymlFilePath = ""
N = 4

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

idItem = 0
matrix = []
dataMatrx = []
matrixLine =["void"]
addToMatrix = False
idItemKey = 0

idLongerItem = 0
idLineBigestWidth = 0
idItemBigestWidth = 0
idLineBigestHight = 0
idItemBigestHight = 0
LongestWith = 0
idHighestHight = [0,0]
idLongerLine = 0
returnLine = ""

def DisplayList(matrix, idLongerLine, idHighestHightL, idHighestHightC, blockList, baseFileValue,dataMatrx):

    pageWidth = (GetSize("space")[0]*2) + (getLineItemWidth(getItemOnALine(matrix, idLongerLine))) + (len(getItemOnALine(matrix, idLongerLine)) * GetSize("space")[1])
    Hight = (GetSize("space")[0]*2) + GetSize(matrix[idHighestHightC][idHighestHightL][0])[1] + (len(matrix) * GetSize("space")[1])
    idLine = 0
    idItem = 0
    x = 0
    y = 0
    FinalBlock = ""
    linkBlock = ""
    idItemAdd = 0
    nbTrame = 0
    excludedBridgeId = 0

    for matrixLine in matrix:
        lineTotalWidth = getLineItemWidth(getItemOnALine(matrix, idLine))
        space = (pageWidth - lineTotalWidth)/(len(getItemOnALine(matrix, idLine))+1)
        for matrixItem in matrixLine:
            if(matrixItem[0] != "trame"):
                x = GetSize("space")[0] + space*(idItem+1) - (GetSize("space")[0])
            else:
                x = GetSize("space")[0]
            if(idLine > 0):
                if(isATrameOnLineOnly(matrix[idLine-1])):
                    nbTrame=nbTrame+1
                y = GetSize("space")[0] + GetSize("space")[1]*(idLine-nbTrame) + getPreviousItemHight(matrix, idLine) + (GetSize("space")[1]*(nbTrame))/1.5
            else:
                y = GetSize("space")[0]
            if(idItem > 0):
                x = GetSize("space")[0] + space*(idItem+1) + getPreviousItemLength(matrixLine, idItem) - (GetSize("space")[0])
            if(matrixItem[0] == "trame"):
                bridgeId = getObjectOnMatryByTitle(dataMatrx, "bridge_id",excludedBridgeId)
                excludedBridgeId=excludedBridgeId+1
                print("bridgeId: " + str(bridgeId))
                if(bridgeId != ""):
                    FinalBlock = FinalBlock + replaceDataOnTrame(getValueOnFileContent(matrixItem[0], blockList)[1], (str(matrixItem[1] + " | vmbr" + str(bridgeId[1]))), x, y, pageWidth - (2*GetSize("space")[0]),idItemAdd)    
                    #FinalBlock = FinalBlock + replaceDataOnTrame(getValueOnFileContent(matrixItem[0], blockList)[1], (str(matrixItem[1] + " | vmbr" + str(bridgeId[1]))), x, y, pageWidth - (2*GetSize("space")[0]),idItemAdd)    
                else:
                    FinalBlock = FinalBlock + replaceDataOnTrame(getValueOnFileContent(matrixItem[0], blockList)[1], matrixItem[1], x, y, pageWidth - (2*GetSize("space")[0]),idItemAdd)
            else:
                FinalBlock = FinalBlock + replaceDataOnComponent(getValueOnFileContent(matrixItem[0], blockList)[1], matrixItem[1], x, y,idItemAdd)
            matrix[idLine][idItem].append([x,y])
            idItemAdd=idItemAdd+1
            idItem=idItem+1
        idLine=idLine+1
        idItem=0

    displaySeparation()

    idLine = 0
    idItem = 0
    idItemToal = 0
    for matrixLine in matrix:
        for matrixItem in matrixLine:
            if(len(matrixItem) >= 5):
                linkedToIds = matrixItem[3].replace("$link:", "")
                linkedToIds=linkedToIds.split(",")
                linkedToIds=linkedToIds
                for linkedToId in linkedToIds:
                    linkedToId=int(linkedToId)-1
                    linkedToItem = getObjectOnMatryById(matrix, int(linkedToId))
                    linkXY= linkedXY(matrixItem[-1][0], matrixItem[-1][1],idLine,idItemToal,matrixItem[0], linkedToItem[-1][0], linkedToItem[-1][1],getObjectLineById(matrix,linkedToId),linkedToId,getObjectOnMatryById(matrix, linkedToId)[0])
                    if(isATrame(getObjectOnMatryById(matrix, linkedToId)[0])):
                        linkBlock=linkBlock+str(createLinkToTrame(linkXY[0][0],linkXY[0][1], linkXY[1][1], blockList[-1][1], idItemAdd))
                    elif(isATrame(matrixItem[0])):
                        linkBlock=linkBlock+str(createLinkToTrame(linkXY[1][0],linkXY[1][1], linkXY[0][1], blockList[-1][1], idItemAdd))
                    else:
                        linkBlock=linkBlock+str(createLink(linkXY[0][0],linkXY[0][1], blockList[-1][1], idItemAdd,linkXY[1][0],linkXY[1][1]))
                    idItemAdd=idItemAdd+1
            idItem=idItem+1
            idItemToal=idItemToal+1
        idLine=idLine+1
        idItem=0

    for data in dataMatrx:
        if(data[0] != "/link" and data[0] != "/line" and data[0] != ""):
            print(data)

    # on ajoute notre liste de lien au shema mais au début car plus c'est au debut plus c'est en dessous donc les liens seront en dessous des icones
    shemaContent = linkBlock + FinalBlock
    # on ajoute nos formes au fichier de base
    baseFileValue = baseFileValue.replace("$REPLACEME", shemaContent)
    # on change la hauteur du shema
    baseFileValue = baseFileValue.replace("$Hight", str(Hight))
    # on change la largeur du shema
    baseFileValue = baseFileValue.replace("$width", str(pageWidth))
    # on ouvre le fichier de destination (sur le bureau) aprecu.drawio
    file = open(descktopPath, "w")
    # on ecris dans notre fichier le contenu
    file.write(baseFileValue)
    # on ferme le fichier
    file.close

def getItemIdByLine(idLineSearch, idItemSearch, matrix):
    idLine = 0
    idItem = 0
    idItemTotal = 0
    for line in matrix:
        for item in line:
            if(int(idLine) == int(idLineSearch) and int(idItem) == int(idItemSearch)):
                return idItemTotal
            idItemTotal=idItemTotal+1
            idItem=idItem+1
        idLine=idLine+1
    return -1

def getXY(item):
    return item[-1]

def linkedXY(startx, starty, startIdLine, startId, startItemId, finalx,finaly,finalIdLine, finalId, finalItemId):
    if(startIdLine == finalIdLine):
        starty = starty + (GetSize(startItemId)[1])/2
        finaly = finaly + (GetSize(startItemId)[1])/2
        if(startId > finalId):
            startx = startx + GetSize("margin")
            finalx = startx  + GetSize(finalItemId)[0] + GetSize("space")[0]
        else:
            finalx = finalx + GetSize("margin")
            startx = startx + GetSize(startItemId)[0] - GetSize("margin")
    elif(startIdLine > finalIdLine):
        startx=startx + (GetSize(startItemId)[0])/2
        finalx=finalx + (GetSize(finalItemId)[0])/2
        starty=starty + GetSize("margin")
        finaly=finaly+(GetSize(finalItemId)[1]) - GetSize("margin")
    else:
        startx = startx + GetSize(startItemId)[0]/2
        finalx = finalx + GetSize(finalItemId)[0]/2
        starty = starty + GetSize(startItemId)[1] - GetSize("margin")
        finaly = finaly + GetSize("margin")
    return[startx,starty],[finalx,finaly]

def getObjectLineById(matrix, id):
    idLine = 0
    idItem = 0
    for line in matrix:
        for item in line:
            if(int(idItem) == int(id)):
                return idLine
            idItem=idItem+1
        idLine=idLine+1
    return ""

def getObjectOnMatryById(matrix, id):
    idItem = 0
    for line in matrix:
        for item in line:
            if(int(idItem) == int(id)):
                return item
            idItem=idItem+1
    return ""

def getObjectOnMatryByTitle(matrix, title, exclude):
    idBridge = 0
    if((matrix[0]) != list):
        for item in matrix:
            if(title == item[0]):
                print(item)
                print("idBridge: " + str(idBridge))
                print("exclude: " + str(exclude))
            if(title == item[0] and idBridge >= exclude):
                return item
            if(item[0] == title):
                idBridge=idBridge+1
    else:
        for line in matrix:
            for item in line:
                if(title == item[0] and idBridge >= exclude):
                    return line
                idBridge=idBridge+1
    return ""

def getHighesItemOnLine(line):
    highestItemId = 0
    idItem = 0
    for item in line:
        if (GetSize(item[0])[1] > GetSize(line[highestItemId][0])[1]):
          highestItemId = idItem
    idItem=idItem+1
    return GetSize(line[highestItemId][0])[1]

def getPreviousItemLength(line, idItem):
    idItemInLine = 0
    totalWidth = 0
    for item in line:
        if(idItemInLine < idItem):
            totalWidth=totalWidth+GetSize(item[0])[0]
        idItemInLine=idItemInLine+1
    return totalWidth

def getPreviousItemHight(matrix, idLine):
    idLineInMatrix = 0
    totalHight = 0
    isATrameVar = 0
    for line in matrix:
        if(isATrame(line[idItem][0]) and isATrameVar != 2):
            isATrameVar = 1
        else:
            isATrameVar = 2
        if(idLineInMatrix < idLine):
            totalHight=totalHight+getHighesItemOnLine(line)
        idLineInMatrix=idLineInMatrix+1
    return totalHight

def lineHasATrame(line):
    hasATrame = False
    for item in line:
        if(item[0] == "trame"):
            hasATrame = True
    return hasATrame

def getItemOnALine(allItems, idLineSearch):
    idLine = 0
    for line in allItems:
        if (idLine == idLineSearch):
            return line
        idLine=idLine+1
    return ""

def isAnItem(id):
    itemList = ["trame","switch","router","firewall","wan","server","client"]
    for item in itemList:
        if (item == id):
            return True
    return False

def getLineItemWidth(items):
    if(len(items) == 0):
        return ""
    lineItemWidth = 0
    for item in items:
        lineItemWidth = lineItemWidth + GetSize(item[0])[0]

    return lineItemWidth

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

def createLinkToTrame(startX, startY, finalY, linkBlock, linkid):
    finalX = startX
    linkBlock = linkBlock.replace("$id", str(linkid))#id de la liaison
    linkBlock = linkBlock.replace("$xStart", str(startX))#id du début de la liaison(x) 
    linkBlock = linkBlock.replace("$yStart", str(startY))#id du début de la liaison(y)
    linkBlock = linkBlock.replace("$xEnd", str(finalX))#id de la fin de la liaison(x) 
    linkBlock = linkBlock.replace("$yEnd", str(finalY))#id de la fin de la liaison(y)

    return linkBlock



def createLink(startX, startY, linkBlock, linkid, finalX, finalY):
    linkBlock = linkBlock.replace("$id", str(linkid))#id de la liaison
    linkBlock = linkBlock.replace("$xStart", str(startX))#id du début de la liaison(x) 
    linkBlock = linkBlock.replace("$yStart", str(startY))#id du début de la liaison(y)
    linkBlock = linkBlock.replace("$xEnd", str(finalX))#id de la fin de la liaison(x) 
    linkBlock = linkBlock.replace("$yEnd", str(finalY))#id de la fin de la liaison(x) 
    linkBlock = linkBlock.replace("$Aa", str(linkid))#id de la fin de la liaison(x) 

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
    textAreaSize = [100,30]
    space = [25,50]
    margin = 15
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
            # si c'est le marges
            case "space":
               return space
            # si c'est uen trame
            case "trame":
               return trameSize
        # si c'est le marges
            case "margin":
               return margin
            # si c'est une zone de text
            case "textArea":
               return textAreaSize
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
    
def isATrameOnLineOnly(line):
    for item in line:
        print(item[0])
        if(not isATrame(item[0])):
            return False
    return True


def matchingDataWithId(data):
    match data:
            # si c'est le serveur
            case "srv_name":
                return "server"
            # si c'est le serveur
            case "srvappl_name":
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
            # si c'est le wan
            case "bridge_netid":
               return "trame"
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
    string = string.replace(" ", "")
    if string[0] == "'" or string[0] == "\"": 
        string = string[1:]
    if string[len(string)-1] == "'" or string[len(string)-1] == "\"":
        string = string[:-1]
    return string.replace("\n", "")

def testRegexValue(regex, value):
    return bool(re.match(regex, value))

def matchTitleWithComment(titlesArray):
    titleList = [["daysuse","Nombre de jour d'utilisation: "],
                        ["project_name","Nom du projet: "],
                        ["srv_name","Nom du serveur: "],
                        ["cli_name","Nom du client: "],
                        ["srvappl_name","Nom du serveur applicatif: "],
                        ["bridge_netid","netId du reseau: "],
                        ["domain_name","Nom du domaine: "],
                        ["domain_admin_password","Mot de passe de l'admin du domaine: "],
                        ["recovery_password","Mot de passe de récuperation: "],
                        ["rt_name","Nom du routeur: "],
                        ["upn","UON: "],
                        ["firstname","Prenom: "],
                        ["surname","Nom: "],
                        ["display_name","Nom affiché: "],
                        ["user_password","Mot de passe de l'utilisateur: "],
                        ["email","Email: "],
                        ["bridge_id","Id du reseau: "],
                        ["wan_ip","Ip du wan: "],]
    for title in titlesArray:
        for titleComment in titleList:
            if(title == titleComment[0]):
                return titleComment[1]
    return""

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

if(len(sys.argv) < 2 and ymlFilePath != ""):
    print("veuillez indiquer le chemin du fichier .yml en paramètre")
else:
    # get length of string
    length = len(ymlFilePath)
    # create a new string of last N characters
    Str2 = ymlFilePath[length - N:]
    # print Last 4 characters
    if(Str2 != ".yml"):
        print("le fichier que vous avez passé en paramètre n'est pas un fichier .yml")  
        print("veuillez renseigner le chemin du fichier .yml en paramètre")
    elif(not os.path.isfile(ymlFilePath)):
        print("le chemin qu vous avez passé en paramètre n'existe pas") 
        print("veuillez renseigner le chemin du fichier .yml en paramètre")
    else:
        # on test si il y a un fichier .yml dans le repertoire
        if(len(ymlFilePath) <= 0):
            # si non on affiche un message d'erreur
            print("veuilliez ajouter un fichier .yml à coté du script")
        else:
            #si oui on commence le script

            # tableau contenant la liste des donée erronées
            errorArray = []
            #tableau contenant la liste des valeur(array[1]) et de leur clé(array[0])
            keyValueArray = []
            # on recupère le contenu du fichier .yml qu'on a trouvé
            fileContent = open(ymlFilePath).read()
            # on edit le contenu du fichier pour en faire un tableau et que les donées soient lisibles et utilisables
            fileContent = fileContent.split("\n")
            # on passe par chaque case du tableau
            idLine = 0
            for line in fileContent:
                line = (line.split("#")[0]).split(":")
                if(line[0] != ""):
                    line[0] = CleanString(line[0])
                if(len(line) > 1):
                    if(line[1] != ""):
                        line[1] = CleanString(line[1])
                if(matchingDataWithId(line[0]) != ""):
                    matrixLine.append([matchingDataWithId(line[0]),line[1], idItem])
                    idItem=idItem+1
                else:
                    dataMatrx.append(line)
                if(line[0] == "/line" or idLine == len(fileContent)-1):
                    addToMatrix = True
                if(line[0] == "/link"):
                    matrixLine[-1].append("$link:" + str(line[1]))
                if(addToMatrix):
                    del matrixLine[0]
                    matrix.append(matrixLine)
                    addToMatrix = False 
                    matrixLine=["void"]
                idLine=idLine+1

                """
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
                """

#           
#            print("matrix:")
#            for line in matrix:
#                print(line)

#            displaySeparation()

        coponents = open(coponentFilePath).read()
        # separe par composant
        coponents = coponents.split("|")

        blockList = []

        for component in coponents:
            component = component.split("!")
            blockList = blockList + [[component[0].replace("\n", ""), component[1]]]
            if(component[0].replace("\n", "") == "returnLine"):
                returnLine = component[1]


        if(len(matrix) > 0):
            id = 0
            lineId = 0
            itemId = 0
        for matrixLine in matrix:
            lineTotalWidth = getLineItemWidth(getItemOnALine(matrix, lineId))
            if(int(lineTotalWidth) > getLineItemWidth(getItemOnALine(matrix, idLongerLine)) and not lineHasATrame(matrixLine)):
                idLongerLine = lineId
            for matrixItem in matrixLine:                
                if(GetSize(matrix[idHighestHight[0]][idHighestHight[1]][0])[1] <  GetSize(matrixItem[0])[1]):
                    idHighestHight[0] = lineId
                    idHighestHight[1] = itemId
                idItem=idItem+1
            lineId=lineId+1
            idItem=0
        print("----------------------------------------------")
        DisplayList(matrix, idLongerLine, idHighestHight[1], idHighestHight[0], blockList, baseFileValue,dataMatrx)
        print("._._._._._._._._._._._._._._._._._._._._._._.")
        print(returnLine)