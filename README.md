# But
Le but est de créer un simple script qui récupère des données dans un fichier `.yml` et les met sur un schema `drawIo`.  
Le Script peut tourner sur une machine windows 10 et une machine ubuntu 22.xx, avec l'interpreteur python.

#### `Le Schema sans les données :`
![shema1](imageForReadMe/aprecu1.png)
---
#### `Le Schema avec les donées :`
![shema2](imageForReadMe/aprecu2.png)

# Fichiers

### script python  
script qui test les valeurs du fichier `.yml`

![script](imageForReadMe/scriptTest.png)

script qui gènere le shema (fichier `apercu.drawio`)

![script](imageForReadMe/script.png)

fichier contenant les donées à testet et à ajouter dans le schema  
![yml](imageForReadMe/yml.png)

dossier contenant des fichiers `.txt` servant à la génération du schema  
![component](imageForReadMe/component.png)
![txtFiles](imageForReadMe/txtFiles.png)
# Fonctionnement

### script 1 (`testValue.py`)

Le script va récupèrer les données dans le fichier `*.yml` qui doit être dans le même répértoire que le script et les tester pour voir si elle respectent le format défini.  
Si toutes les donées respéctent leur format alors l'output sera `True` si les données sont fausse l'outbupt sera `False`, en resumé:
`Faute` => `False`  
`Juste` => `True`

![yml](imageForReadMe/yml.png)

### script 2 (`createShema.py`)

Le script fonctionne avec 1 paramètre qui est le chemin du fichier `.yml`, exemple:

Sur Windows:  
`>> C:\Users\Public\createShema.py C:\Users\Public\aFolder\data.yml`

Sur Ubuntu:  
`>> \home\Public\createShema.py \home\Public\\aFolder\data.yml`

#### Il y a différents messages d'erreur:

 Si le chemin du fichier n'est pas renseigné, exemple:  
`>> C:\Users\Public\createShema.py`  
![errorNoParameter](imageForReadMe/errorNoParameter.png)  


Si le chemin du fichier n'est pas un fichier `.yml`, exemple:  
`>> C:\Users\Public\createShema.py C:\Users\Public\aFolder\data.txt`   
![errorNotYml](imageForReadMe/errorNotYml.png)

Si le chemin du fichier n'existe pas, exemple:  
`>> C:\Users\Public\createShema.py 5:\Users\Public\aFolder\data.txt`   
![errorYmlNotExist](imageForReadMe/errorYmlNotExist.png)

---

Le fichier yml à ce format:  
![ymlContent](imageForReadMe/ymlContent.png)

---

Quand tout ça est fini le fichier .drawio est généré et déposé sur le bureau.  
![drawIoFile](imageForReadMe/drawIoFile.png)