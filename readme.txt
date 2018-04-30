#Création de Carte de village

La carte du village de Saint-Georges-en-Couzan a été créée avec les outils suivants :
 - données OpenStreetMap (licence ODbL)
 - modifications locales sous JOSM
 - traitement des modifications par les scripts python compare/to_renderer
 - rendus sous Maperitive 
 - assemblage sous Gimp

Les éléments fournis ici sont :
Les scripts pythons, compare.py pour comparer un fichier de données OSM brutes avec un fichier modifié en local, qui crée des trois fichiers .txt add/delete/offset décrivant ces modifications. Le script to_renderer.py applique ces modifications à un fichier OSM (utile pour profiter de contributions plus récentes sous OSM malgré des modifications locales sur un fichier ancien).
Les fichiers de données locaux global, situation pour les encarts complémentaires à la carte, ainsi que stg_suppl et bourg_suppl pour afficher des données supplémentaires sur les cartes.

Le rendu sous Maperitive est possible avec les feuilles de styles .mrules, la principale saintgeorges.mrules. Modifiée par to_renderer, elle devient saintgeorges_post.mrules. Situation et global permettent de rendre les encarts de situation et de répartition des hameaux.

L'assemblage final a été réalisé sous Gimp.

Licences : les données géographique des fichiers .osm sont dérivées de données OpenStreetMap et sont donc sous licence ODbL.
Les scripts python sont sous licence licence FTWPL (Licence publique + non responsabilité), sauf osmdata.py sous licence GPL v3.
Les feuilles de style sont sous licence CC-by-sa 4.0.
Les icones sont sous licence CC0.