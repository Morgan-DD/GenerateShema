# But
Le but est de créer un simple script qui récupère des données dans un fichier `.yml` et les met sur un schema `drawIo`.  
Le Script peut tourner sur une machine windows 10 et une machine ubuntu 22.xx, avec l'interpreteur python.

#### `Le Schema avant le script :`
![shema1](imageForReadMe/aprecu1.png)
---
#### `Le Schema apres le script :`
![shema2](imageForReadMe/aprecu2.png)

# Fichiers

script python  
![script](imageForReadMe/script.png)

fichier contenant les donées à ajouter dans le schema  
![yml](imageForReadMe/yml.png)

dossier contenant des fichiers `.txt` servant à la génération du schema  
![component](imageForReadMe/component.png)
![txtFiles](imageForReadMe/txtFiles.png)

# Fonctionnement

Le script va récupèrer les données dans le fichier `*.yml` qui doit être dans le même répértoire que le script.  
![yml](imageForReadMe/yml.png)

Si le script ne trouve pas de fichier `*.yml` il va afficher ce message d'erreur :  
![errorNoYml](imageForReadMe/errorNoYml.png)

---

Le fichier yml à ce format:  
![ymlContent](imageForReadMe/ymlContent.png)

---

Le script verifier les donées et si elle convienne à des paramètres

Si une des valeurs ne respecte pas les regles un message d'erreur sera affiché:  
![errorymlContent](imageForReadMe/errorymlContent.png)

Quand tout ça est fini le fichier .drawio est généré et déposé sur le bureau.  
![drawIoFile](imageForReadMe/drawIoFile.png)