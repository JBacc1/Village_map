# -*- coding: utf-8 -*-
# Code par JB (https://www.openstreetmap.org/user/JBacc1) sous licence FTWPL (Licence publique + non responsabilité)

#Compare deux fichiers OSM, l'un original, l'autre qui part du même et qui a été modifié à la main (sous JOSM, par exemple). Après comparaison, crée 3 fichiers de "diff" utilisé par le script to_renderer.py qui semi-automatise la réapplication de ces modifications.

import sys, time
from osmdata import *

try : file_pre,file_post=sys.argv[1],sys.argv[2]
except: 
	print("Usage : python compare_osm.py infile_pre.osm infile_post.osm [rw], rw si supprime les fichiers existant, sinon, complétés en append.")
	sys.exit()

REWRITE=False
try: REWRITE= sys.argv[3].lower()=="rw"
except: pass
if REWRITE: rw="w"
else: rw="a"

DELETE_TO_NO_TAGS=True #Si l'élément est supprimé dans _post, les tags seront supprimés par la suite (les éléments ne sont pas supprimables).

VERBOSE=True
TAGS_WITH_SPACES=["name","description","to_target","to_element","wikipedia"]

def compare_tags(pre,post):
	"""Appel : element._tags._dict, retour : add,delete listes"""
	add,delete=[],[]
	for key in list(post.keys()):
		if key in list(pre.keys()):
			if post[key]!=pre[key]:
				add.append((key,post[key]))
		else: add.append((key,post[key]))
	for key in list(pre.keys()):
		if not(key in list(post.keys())):
			delete.append(key)	
	return add,delete
	
def add2add_file(file,object_type,id,tag_list):
	line=object_type.lower().strip()+ " " +str(id) + " "
	for tag in tag_list:
		if tag[0] in TAGS_WITH_SPACES: line+=tag[0].strip()+ "=" + tag[1].replace(" ","_")+" "
		else: line+=tag[0].strip()+ "=" +tag[1].strip()+" " 
	line+="\n"
	file.write(line)
def add2delete_file(file,object_type,id,tag_list):
	line=object_type.lower().strip()+ " " +str(id) + " "
	for tag in tag_list:
		line+=tag.strip()+" " 
	line+="\n"
	file.write(line)
def add2offset_file(file,object_type,id,loc):
	line=object_type.lower().strip()+ " " +str(id) + " "
	line+="m"+str(loc.x)+" m"+str(loc.y)
	line+="\n"
	file.write(line)
	

print("Script compare_osm.py de JB (https://www.openstreetmap.org/user/JBacc1) sous licence FTWPL.")
t0=time.time()
print(time.strftime("%a %H:%M",time.localtime(t0)))

osm_pre,osm_post=OsmData(),OsmData()
print("Chargement : "+file_pre, end=" ", flush=True)
osm_pre.load_xml_file(file_pre)
t1=time.time()
print(str(round(t1-t0,1))+"s")
print("Chargement : "+file_post, end=" ", flush=True)
osm_post.load_xml_file(file_post, keep_detail=True, drop_deleted=False)
t2=time.time()
print(str(round(t2-t1,1))+"s")

##$$ Voir pour keep_details

add_file=file_pre.replace(".osm","_add.txt")
delete_file=file_pre.replace(".osm","_delete.txt")
offset_file=file_pre.replace(".osm","_offset.txt")

with open(add_file,rw,encoding='utf-8') as addf, open(delete_file,rw,encoding="utf-8") as deletef, open(offset_file,rw,encoding='utf-8') as offsetf:

	print("Comparaison des éléments")
	count=0
#NODES
	for node_post in osm_post.find_nodes(lambda x: True):
		count+=1
		if VERBOSE and count%25000==0: print(str(count)+" éléments traités")
		try: node_pre=osm_pre.node(node_post.id)
		except: 
			if VERBOSE: print("node "+str(node_post.id)+" non contenue dans le fichier initial : "+file_pre)
		if node_pre.id==node_post.id:
			if not node_pre._tags.equals(node_post._tags):
#			print("TAGS",node_pre.id,node_post.id,node_pre.tags,node_post.tags)
				add,delete=compare_tags(node_pre._tags._dict,node_post._tags._dict)
#			print(add,delete)
				if len(add)>0: add2add_file(addf,"node",node_pre.id,add)
				if len(delete)>0: add2delete_file(deletef,"node",node_pre.id,delete)
			if not node_pre.location.equals(node_post.location):
				add2offset_file(offsetf,"node",node_post.id,node_post.location)
#			print("LOCATION",node_pre.location.x,node_post.location.x,node_pre.tags)
			if node_post.action=="delete":
				delete=[a[0] for a in node_pre.tags]
				if len(delete)>0: add2delete_file(deletef,"node",node_pre.id,delete)
	del node_pre, node_post
#WAYS	
	for way_post in osm_post.find_ways(lambda x: True):
		if VERBOSE and count%25000==0: print(str(count)+" éléments traités")
		try: way_pre=osm_pre.way(way_post.id)
		except: 
			if VERBOSE: print("way "+str(way_post.id)+" non contenu dans le fichier initial : "+file_pre)
		if way_pre.id==way_post.id:
			if not way_pre._tags.equals(way_post._tags):
	#			print("TAGS",way_pre.id,way_post.id,way_pre.tags,way_post.tags)
				add,delete=compare_tags(way_pre._tags._dict,way_post._tags._dict)
	#			print(add,delete)
				if len(add)>0: add2add_file(addf,"way",way_pre.id,add)
				if len(delete)>0: add2delete_file(deletef,"way",way_pre.id,delete)
			if way_post.action=="delete":
				delete=[a[0] for a in way_pre.tags]
				if len(delete)>0: add2delete_file(deletef,"way",way_pre.id,delete)
	del way_pre, way_post
#RELATIONS
	for relation_post in osm_post.find_relations(lambda x: True):
		if VERBOSE and count%25000==0: print(str(count)+" éléments traités")
		try: relation_pre=osm_pre.relation(relation_post.id)
		except: 
			if VERBOSE: print("relation "+str(relation_post.id)+" non contenue dans le fichier initial : "+file_pre)
		if relation_pre.id==relation_post.id:
			if not relation_pre._tags.equals(relation_post._tags):
	#			print("TAGS",relation_pre.id,relation_post.id,relation_pre.tags,relation_post.tags)
				add,delete=compare_tags(relation_pre._tags._dict,relation_post._tags._dict)
	#			print(add,delete)
				if len(add)>0: add2add_file(addf,"relation",relation_pre.id,add)
				if len(delete)>0: add2delete_file(deletef,"relation",relation_pre.id,delete)
			if relation_post.action=="delete":
				delete=[a[0] for a in relation_pre.tags]
				if len(delete)>0: add2delete_file(deletef,"relation",relation_pre.id,delete)
t3=time.time()
print("Temps total : "+str(round(t3-t0,1))+"s")
print("OK")