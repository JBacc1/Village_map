# -*- coding: utf-8 -*-

# Définit les angles de dessin pour des points contenant des tags spécifiques sur des chemins ayant également des tags définis.
# Code par JB (https://www.openstreetmap.org/user/JBacc1) sous licence FTWPL (Licence publique + non responsabilité)

import math, time
import sys
import os.path
from osmdata import *

t0=time.time()

#def_file_ponw="C:/OSM/Maperitive/R25/Python/ponw_def.txt"
DEF_PONW="""highway;barrier
	waterway:stream,river ; waterway:dam,weir,waterfall,lock_gate
	waterway;lock:yes
	aerialway;aerialway
	bridge;end_of:bridge;no""".split("\n")
##$$$power/line…

#PWE: noeuds de fin de way : par exemple ('brigde',["aqueduc","movable"])
combinaisons_pwe=[('bridge', []),('tunnel',[]),("test",["yes","petre","pas_non"])]
onway_main_keys=['railway','highway','waterway','aerialway','barrier']
onway_secondary_keys=['tracktype','lanes','trail_visibility','smoothness','service', 'footway', 'subway','operator','tunnel']

dtag_list_file='delete_tags.txt'
atag_list_file='add_tags.txt'

offset_file='offset.txt'
verbose=True
TAGS_WITH_SPACES=["name","description","to_target","to_element"]

try : in_file=sys.argv[1]
except: 
	print("Usage : python add_angles.py infile.osm [pre[=prefixe]], pre si utilisation du prefixe de fichier pour les fichiers de modification")
	sys.exit()
try : 
	pre=sys.argv[2]
	if pre.lower()[0:3]=="pre":
		if pre.find("=")<0:
			dtag_list_file=in_file.replace(".osm",'_delete.txt')
			atag_list_file=in_file.replace(".osm",'_add.txt')
			offset_file=in_file.replace(".osm",'_offset.txt')
		else:
			pre=pre[pre.find("=")+1:]
			dtag_list_file=pre+'_delete.txt'
			atag_list_file=pre+'_add.txt'
			offset_file=pre+'_offset.txt'
			
except: 
	"Pas d'option 'pre', utilisation des fichiers 'add_tags.txt', 'delete_tags.txt', 'offset.txt'"


def read_kv(s):
	"""Lit un tag sous la forme key:value1,value2… et renvoit (key,[value1,value2]"""
	if s.count(":")==0:
		key=s
		values=[]
	elif s.count(":")>=2:
		print("La définition d'un couple kv doit comprendre un double-point au maximum, par exemple « highway:path,track »). La définition « "+s+" » a été ignorée")
		return("",[])
	else:
		[key,v]=str.split(s,":",1)
		values=[str.strip(a) for a in str.split(v,",")]
	key=str.strip(key)
	return (key,values)

def key_values(s):
	"""retourne un tableau de couples ((ak,[av]),(bk,[bv]),boolean) où ak est la clef du chemin, av la table de valeurs. av=[] si toutes les valeurs sont acceptées. b pour les points sur a. True pour valeurs sur 180°, False pour 360°"""
	ab=str.split(s,";")
	if len(ab)!=2 and len(ab)!=3:
		print("La définition doit comprendre exactement une description de chemin et une description de nœud, séparées par un point-virgule, par exemple : « highway:path;barrier», avec éventuellement une troisième valeur booléenne.\nLa ligne « "+s+" » a été ignorée")
		return ("","")
	bool=True
	if len(ab)==3:
		if ab[2].lower().strip() in ["no","false","non","faux"]:
			bool=False
	return ((read_kv(ab[0]),read_kv(ab[1]),bool))

def read_def(def_list):
#	with open(def_list,encoding="utf-8") as f:
#		lines = f.readlines()
	lines=def_list
	lines=[str.lstrip(a.rstrip("\n")) for a in lines]
	l1=[]
	for line in lines:
		if not len(line)==0:
			if not line[0]=="#":
				l1.append(line)
	combinaisons=[key_values(a) for a in l1]
	return combinaisons
def read_offset(filename):
	offset_dict={}
	move_dict={}
	with open(filename,"r",encoding='utf-8') as file:
		for ligne in file:
			if len(ligne.strip())>0:
				if ligne.strip()[0]!="#":
					t=ligne.strip("\n ").split()
					try:
						id=int(t[1])
						if t[0]=="node": 
							if t[2][0].lower()=="m" and t[3][0].lower()=="m":
								x,y=float(t[2].lower().strip("m")),float(t[3].lower().strip("m"))
								move_dict[id]=(x,y)
							else:
								x,y=float(t[2]),float(t[3])
								offset_dict[id]=(x,y)
						else: print("("+filename+")Ligne non traitée (type d'objet non pris en charge) : "+ligne.strip("\n"))
					except:
						print("("+filename+")Ligne non traitée (identifiant non entier ou offset non décimal) : "+ligne.strip("\n"))
	return offset_dict,move_dict
def read_tag_file(filename):
	lnodes,lways,lrels={},{},{}
	with open(filename,"r",encoding='utf-8') as file:
		for ligne in file:
			if len(ligne.strip())>0:
				if ligne.strip()[0]!="#":
					t=ligne.strip("\n ").split(" ")
	#				print(t)
					try:
						id=int(t[1])
						if t[0]=="node": lnodes[id]=t[2:]
						elif t[0]=="way": lways[id]=t[2:]
						elif t[0]=="rel" or t[0]=="relation": lrels[id]=t[2:]
						else: print("("+filename+")Ligne non traitée (type d'objet non défini) : "+ligne.strip("\n"))
					except:
						print("("+filename+")Ligne non traitée (identifiant non entier) : "+ligne.strip("\n"))
#				else: print("("+filename+")Ligne non traitée (commentaire) : "+ligne.strip("\n"))
	return (lnodes,lways,lrels)
					
	
def way_has_comb(way,comb):
	if len(comb[0][1])==0:
		return way.has_tag(comb[0][0])
	else:
		if not way.has_tag(comb[0][0]):
			return False
		else:
			return way.get_tag(comb[0][0]) in comb[0][1]
def way_has_comb_pwe(way,comb):
	if len(comb[1])==0:
		return way.has_tag(comb[0])
	else:
		if not way.has_tag(comb[0]):
			return False
		else:
			return way.get_tag(comb[0]) in comb[1]
def node_has_comb(node,comb):
	if len(comb[1][1])==0:
		return node.has_tag(comb[1][0])
	else:
		if not node.has_tag(comb[1][0]):
			return False
		else:
			return node.get_tag(comb[1][0]) in comb[1][1]
	
def calcul_angle(a,b):
	"""Calcule l'angle à partir de deux nœuds"""
#   θ = atan2(sin(Δlong)*cos(lat2), cos(lat1)*sin(lat2) − sin(lat1)*cos(lat2)*cos(Δlong))
	DLong=-a.location.x+b.location.x
	angle= (360+((-math.atan2(math.sin(DLong)*math.cos(b.location.y), math.cos(a.location.y)*math.sin(b.location.y) - math.sin(a.location.y)*math.cos(b.location.y)*math.cos(DLong))) /math.pi*180))%360
	angle= (360+(-math.degrees(math.atan2(math.sin(math.radians(DLong))*math.cos(math.radians(b.location.y)), math.cos(math.radians(a.location.y))*math.sin(math.radians(b.location.y)) - math.sin(math.radians(a.location.y))*math.cos(math.radians(b.location.y))*math.cos(math.radians(DLong)) ) )))%360

#	print(angle)
	return angle
def set_angle(n,aa,bb=True):
	"""Enregistre l'angle aa dans le tag approprié et recalcule directement l'angle final"""
	if not n.has_tag("aangle"):
		n.set_tag("aangle",str(round(aa)))
		n.set_tag("angle",str(-round(aa) %180))
		if not bb: n.set_tag("angle",str(-round(aa) %360))
	elif not n.has_tag("bangle"):
		n.set_tag("bangle",str(round(aa)))
		try:
			n.set_tag("angle",str(-round(((aa+float(n.get_tag("aangle")))/2+90)) %180))
			if not bb: n.set_tag("angle",str(-round(((aa+float(n.get_tag("aangle")))/2+90)) %360))
		except:
			n.set_tag("has_angle","False")
	else:
		n.set_tag("has_angle","False")
def set_onway(n,key,value):
	n.set_tag("onway_key",key)
	n.set_tag("onway_value",value)
	return
def node_set_tags(node,tag_list):
	for tag in tag_list:
		node.set_tag(tag[0],tag[1])
def get_kv_from_string(t):
	kv=t.split('=')
	if len(kv)!=2: 
		print('tag ignoré, mal conditionné en "key=value" : "'+t+'"')
		raise ValueError("Tag mal conditionné")
	else: 
		if kv[0] in TAGS_WITH_SPACES: kv[1]=kv[1].replace("_"," ").replace("&amp;#xD","&#xD").replace("&amp;&amp;","&#xD;")
		return kv[0],kv[1]

def is_target(line):
	if line.replace(" ","").find("target:")>=0: return True
	else: return False
def get_target(line):
	return line.strip().replace(" ","").split(":")[1]
def is_element(line):
	if line.replace(" ","").find("draw:")>=0: return True
	else: return False
	
		
print("Script to_renderer.py de JB (https://www.openstreetmap.org/user/JBacc1) sous licence FTWPL.")
print(time.strftime("%a %H:%M",time.localtime(t0)))
	
combinaisons_ponw=read_def(DEF_PONW)
#print(combinaisons_ponw)

# Look for the first OSM map source
print('Chargement du fichier : '+in_file, end=" ", flush=True)
osm = OsmData()
osm.load_xml_file(in_file)
osm.upload="never"
t1=time.time()
print(str(round(t1-t0,1))+"s")
	
#Vérifie si un nœud a déjà une information d'orientation ou de fin
for node in osm.find_nodes(lambda x: (x.has_tag("angle") and not x.has_tag("has_angle")) or x.has_tag("end_of")):
#	raise AssertionError("Cette couche contient déjà des informations d'orientation. Exécution stoppée.")
	print("Cette couche contient déjà des informations d'orientation. Des choses étranges peuvent se produire !")
	break
##$$ voir si on supprime ces informations.

i=0	
##3ème partie : modifie les tags 
print("Modification de tags")
(dnodes,dways,drelations)=read_tag_file(dtag_list_file)
(anodes,aways,arelations)=read_tag_file(atag_list_file)

for id in list(dnodes.keys()):
	if osm.has_node(id):
		for key in dnodes[id]:
			osm.node(id).remove_tag(key)
	elif verbose: print("delete_tag : node absent : "+str(id))
for id in list(dways.keys()):
	if osm.has_way(id):
		for key in dways[id]:
			osm.way(id).remove_tag(key)
	elif verbose: print("delete_tag : way absent : "+str(id))
for id in list(drelations.keys()):
	if osm.has_relation(id):
		for key in drelations[id]:
			osm.relation(id).remove_tag(key)		
	elif verbose: print("delete_tag : relation absente : "+str(id))

for id in list(anodes.keys()):
	if osm.has_node(id):
		for tag in anodes[id]:
			kv=get_kv_from_string(tag)
			osm.node(id).set_tag(kv[0],kv[1])
	elif verbose: print("add_tag : node absent : "+str(id))
for id in list(aways.keys()):
	if osm.has_way(id):
		for tag in aways[id]:
			kv=get_kv_from_string(tag)
			osm.way(id).set_tag(kv[0],kv[1])
	elif verbose: print("add_tag : way absent : "+str(id))
for id in list(arelations.keys()):
	if osm.has_relation(id):
		for tag in arelations[id]:
			kv=get_kv_from_string(tag)
			osm.relation(id).set_tag(kv[0],kv[1])
	elif verbose: print("add_tag : relation absente : "+str(id))

###4ème partie : décale les points demandés
print("Décalage des noeuds spécifiés")
offset_dict,move_dict=read_offset(offset_file)
for id in list(offset_dict.keys()):
	if osm.has_node(id):
		osm.node(id).location.offset_meters(offset_dict[id][0],offset_dict[id][1])
	elif verbose: print("offset_node : node absent : "+str(id))
for id in list(move_dict.keys()):
	if osm.has_node(id):
		osm.node(id).location.move_to(move_dict[id][0],move_dict[id][1])
	elif verbose: print("move_node : node absent : "+str(id))

###Première partie, on ajoute les informations de fin de chemin.
print("Recherche des extrémités d'éléments")
for comb in combinaisons_pwe:
	#Parcourt les nœuds de chaque way pour trouver les éléments recherchés, dans ce cas, calcule les angles à réutiliser ensuite
	for way in osm.find_ways(lambda x: x.has_tag(comb[0])):
		if way_has_comb_pwe(way,comb):
			w=''
			for wk in onway_main_keys:
				if way.has_tag(wk): w=wk
			tags=[]
			for tkv in onway_secondary_keys:
				if way.has_tag(tkv): tags.append((tkv,way.get_tag(tkv)))
			#1er node
			if osm.node(way.nodes[0]).has_tag("end_of"):
				if osm.node(way.nodes[0]).has_tag("end_of",comb[0]):
					osm.node(way.nodes[0]).set_tag("end_of","no")
			else:
				osm.node(way.nodes[0]).set_tag("end_of",comb[0])
				if w!='':
					osm.node(way.nodes[0]).set_tag("onway_end_key",w)
					osm.node(way.nodes[0]).set_tag("onway_end_value",way.get_tag(w))
#					print(w,way.get_tag(w))
				if len(tags)!=0:
					node_set_tags(osm.node(way.nodes[0]),tags)
			#dernier node
			if osm.node(way.nodes[way.nodes_count-1]).has_tag("end_of"):
				if osm.node(way.nodes[way.nodes_count-1]).has_tag("end_of",comb[0]):
					osm.node(way.nodes[way.nodes_count-1]).set_tag("end_of","no")
			else:
				osm.node(way.nodes[way.nodes_count-1]).set_tag("end_of",comb[0])
				if w!='':
					osm.node(way.nodes[way.nodes_count-1]).set_tag("onway_end_key",w)
					osm.node(way.nodes[way.nodes_count-1]).set_tag("onway_end_value",way.get_tag(w))
				if len(tags)!=0:
					node_set_tags(osm.node(way.nodes[way.nodes_count-1]),tags)
	
	
###Partie 2, on ajoute les informations d'angle	
print('Calcul des angles des éléments')
for comb in combinaisons_ponw:
	#Parcourt les nœuds de chaque way pour trouver les éléments recherchés, dans ce cas, calcule les angles à réutiliser ensuite
	for way in osm.find_ways(lambda x: x.has_tag(comb[0][0])):
		if way_has_comb(way,comb):
			#1er node
			if node_has_comb(osm.node(way.nodes[0]),comb):
				aa=calcul_angle(osm.node(way.nodes[1]),osm.node(way.nodes[0]))
				set_angle(osm.node(way.nodes[0]),aa,comb[2])
				set_onway(osm.node(way.nodes[0]),comb[0][0],way.get_tag(comb[0][0]))
			#autres nodes
			for i in list(range(1,way.nodes_count-1)): # range à count-1 pour aller à count-2 !
				if node_has_comb(osm.node(way.nodes[i]),comb):
					aa=calcul_angle(osm.node(way.nodes[i-1]),osm.node(way.nodes[i]))
					set_angle(osm.node(way.nodes[i]),aa,comb[2])
					aa=calcul_angle(osm.node(way.nodes[i+1]),osm.node(way.nodes[i]))
					set_angle(osm.node(way.nodes[i]),aa,comb[2])
					set_onway(osm.node(way.nodes[i]),comb[0][0],way.get_tag(comb[0][0]))
			#dernier node
			if node_has_comb(osm.node(way.nodes[way.nodes_count-1]),comb):
				aa=calcul_angle(osm.node(way.nodes[way.nodes_count-2]),osm.node(way.nodes[way.nodes_count-1]))
				set_angle(osm.node(way.nodes[way.nodes_count-1]),aa,comb[2])
				set_onway(osm.node(way.nodes[way.nodes_count-1]),comb[0][0],way.get_tag(comb[0][0]))
	

##Gestion de la feuille de style
print("Modification de la feuille de style")
rules_pre="rando.mrules"
rules_pre_location="C:/OSM/Maperitive/Rules/"
rules_post=rules_pre.replace(".mrules","_post.mrules")
rules_pre="saintgeorges.mrules"
rules_pre_location="C:/OSM/Maperitive/stg/"
rules_post=rules_pre.replace(".mrules","_post.mrules")

rnodes,rways,rrelations={},{},{}
targets={}

for node in osm.find_nodes(lambda x: x.has_tag("to_target")):
	rnodes[node.id]=[node.get_tag("to_target"),node.get_tag("to_element")]
	if (node.get_tag("to_target").replace(" ",""),node.get_tag("to_element").split(";")[0]) not in list(targets.keys()): 
		targets[(node.get_tag("to_target").replace(" ",""),node.get_tag("to_element").split(";")[0])]=[]
	if node.has_tag("name"): n=node.get_tag("name")
	else: n=""
	targets[node.get_tag("to_target").replace(" ",""),node.get_tag("to_element").split(";")[0]].append([node.id,n,node.get_tag("to_element").replace("&quot;",'"').split(";")[1:]])
	node.set_tag("id",str(node.id))
for way in osm.find_ways(lambda x: x.has_tag("to_target")):
	rways[way.id]=[way.get_tag("to_target"),way.get_tag("to_element")]
	if (way.get_tag("to_target").replace(" ",""),way.get_tag("to_element").split(";")[0]) not in list(targets.keys()): 
		targets[(way.get_tag("to_target").replace(" ",""),way.get_tag("to_element").split(";")[0])]=[]
	if way.has_tag("name"): n=way.get_tag("name")
	else: n=""
	targets[way.get_tag("to_target").replace(" ",""),way.get_tag("to_element").split(";")[0]].append([way.id,n,way.get_tag("to_element").replace("&quot;",'"').split(";")[1:]])
	way.set_tag("id",str(way.id))
	
#print(targets)

target,element="",""
with open(rules_pre_location+rules_pre,"r",encoding="utf-8") as pre, open(rules_post,"w",encoding="utf-8") as post:
	for line in pre:
		if is_target(line):
			target=get_target(line)
		if is_element(line): element=get_target(line)
		else: element=""
		if (target,element) in list(targets.keys()): post.write("//Ajout automatique par le script to_renderer.py\n")
		
		if (target,element) in list(targets.keys()):
			for t in targets[target,element]:
				paragraph=line[:line.find("draw")]
				r=""
				if t[1]!="": r+=paragraph+"//"+t[1].replace("é","e").replace("&#xD;"," ")+"\n"
				r+=paragraph+"for: id="+str(t[0])+"\n"
				r=r+paragraph+"\t"+"define\n"
				r=r+paragraph+"\t\t"+("\n"+paragraph+"\t\t").join(t[2])+"\n"
				post.write(r)
			del targets[target,element]
		
		
		post.write(line)
#print(targets)

if len(list(targets.keys()))>0:
	print("Certains couples target/élément n'ont pas été trouvés : "+str(sorted(targets.keys())))
	print(targets)

t_1=time.time()
print('Sauvegarde du fichier : '+in_file.replace('.osm','')+"_post.osm", end=" ", flush=True)
osm.save_xml_file(in_file.replace('.osm','')+"_post.osm")
tf=time.time()
print(str(round(tf-t_1,1))+"s")
print("Temps total : "+str(round(tf-t0,1))+"s")
	
print("OK")
