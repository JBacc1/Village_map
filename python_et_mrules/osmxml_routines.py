# -*- coding: utf-8 -*-

# Code fourni par JB : http://osm.org/user/JBacc1 ou @RandoCarto (https://twitter.com/RandoCarto) sous licence  FTWPL - THE FUCK THE WARRANTY PUBLIC LICENCE (public licence + no warranty)

#Package rassemblant des routines/fonctions de traitement de fichiers .osm xml
#Non vérifié en conditions extrêmes, cas tordus non pris en compte, à utiliser comme matériel expérimental !


import math

def is_comment(line):
	if line.strip(" \n\t")[0]=="#": return True
	else: return False

def get_object_id(line):
#	<node id="386238268" changeset="13530767" user="botdidier2020" uid="870861" version="3" timestamp="2012-10-17T11:57:09Z" lat="46.8940554" lon="4.1122585">
	debut=line.find('id="')+4
	fin=line.find('"',debut)
	if fin<0:
		debut=line.find("id='")+4
		fin=line.find("'",debut)
	return int(line[debut:fin])
def get_node_ref(line):
	#    <nd ref='-160028' />
	l=line.strip()
	nd=0
	if l[0:3]=="<nd": 
		debut=line.find('ref="')+5
		fin=line.find('"',debut)
		if fin<0:
			debut=line.find("ref='")+5
			fin=line.find("'",debut)
		nd=int(line[debut:fin])
	return nd
def get_way_ref(line):
#used in create_blocs.py
	#    <member type='way' ref='-179141' role='outer' />
	l=line.strip()
	way=0
	if l[0:18]=="<member type='way'" or l[0:18]=='<member type="way"': 
		debut=line.find('ref="')+5
		fin=line.find('"',debut)
		if fin<0:
			debut=line.find("ref='")+5
			fin=line.find("'",debut)
		way=int(line[debut:fin])
	return way
def get_member(line):
	#    <member type='way' ref='-179141' role='outer' />
	l=line.strip()
	if l[0:8]=="<member ": 
		type=get_tag_value(l,"type")
		ref=int(get_tag_value(l,"ref"))
		role=get_tag_value(l,"role")
		return ref,type,role
	else: return 0
	
def get_object_type(line):
	l=line.strip()
	if l[0:5]=="<node": obj="node"
	elif l[0:4]=="<way": obj="way"
	elif l[0:9]=="<relation": obj="rel"
	else: obj=""
	return obj

def is_object_end(line):
	if line.strip('\n \t')[0:5] in ['</nod','</way','</rel']: return True
	elif get_object_type(line)!="" and line.strip('\n \t')[-2:]=="/>": return True
	else: return False
	
def is_tag(line):
	if line.find('<tag k=')>=0: return True
	else: return False
def get_kv(line):
#    <tag k='created_by' v='JOSM' />
	debut=line.find('k="')+3
	fin=line.find('"',debut)
	if fin<0:
		debut=line.find("k='")+3
		fin=line.find("'",debut)
	k=line[debut:fin]
	
	debut=line.find('v="')+3
	fin=line.find('"',debut)
	if fin<0:
		debut=line.find("v='")+3
		fin=line.find("'",debut)
	v=line[debut:fin]
	return k,v

def get_node_lat_lon(line):
	debut=line.find('lat="')+5
	fin=line.find('"',debut)
	if fin<0:
		debut=line.find("lat='")+5
		fin=line.find("'",debut)
#	print(line,debut,fin,line[debut:fin])
	lat=float(line[debut:fin])
	debut=line.find('lon="')+5
	fin=line.find('"',debut)
	if fin<0:
		debut=line.find("lon='")+5
		fin=line.find("'",debut)
	lon=float(line[debut:fin])
	return(lat,lon)

def is_upload(line):
	if line.find(" upload=")>0:return True
	else: return False
def get_upload(line):
	if line.find(" upload='true'")>0 or line.find(' upload="true"')>0: return True
	elif line.find(" upload='false'")>0 or line.find(' upload="false"')>0: return False
	elif line.find(" upload='never'")>0 or line.find(' upload="never"')>0: return "never"
	else: raise ValueError("Pas de clef upload standard (true, false, never) trouvé dans {}".format(line))
def is_delete(line):
	if (line.find(" action='delete'")>0) or (line.find(' action="delete"')>0): return True
	else: return False

def get_tag_value(line,key):
	if line.find(key+'=')<0: return ""
	debut=line.find(key+'=')+len(key)+2
	fin=line.find('"',debut)
	if fin<0: fin=line.find("'",debut)
#S	print(ligne,key,debut,fin,ligne[debut:fin])
	return line[debut:fin]
	

def _get_bbox(file):
#Disused
	bbox=[360,360,-360,-360]	#minx miny maxx maxy
	with open(file,"r",encoding='utf-8') as osm:
		for ligne in osm: #cherche la déclaration bounds
			if ligne.find("<bounds ")>=0:
				bbox[0]=float(get_tag_value(ligne,"minlon"))
				bbox[2]=float(get_tag_value(ligne,"maxlon"))
				bbox[1]=float(get_tag_value(ligne,"minlat"))
				bbox[3]=float(get_tag_value(ligne,"maxlat"))
				return bbox
			if get_object_type(ligne)=="node":
				(y,x)=get_node_lat_lon(ligne)
				if y<bbox[1]: bbox[1]=y
				if y>bbox[3]: bbox[3]=y
				if x<bbox[0]: bbox[0]=x
				if x>bbox[2]: bbox[2]=x
	return bbox
	
def get_bbox_from_nodes(file,run_on_iron_python=False):
	bb_nodes=[360,360,-360,-360]
	if run_on_iron_python: osm=open(file,"r")
	else: osm=open(file,"r",encoding='utf-8')
	for ligne in osm:
		if get_object_type(ligne)=="node" and not is_delete(ligne):
			(y,x)=get_node_lat_lon(ligne)
			if y<bb_nodes[1]: bb_nodes[1]=y
			if y>bb_nodes[3]: bb_nodes[3]=y
			if x<bb_nodes[0]: bb_nodes[0]=x
			if x>bb_nodes[2]: bb_nodes[2]=x
	osm.close()
	return(bb_nodes)
	
def get_bboxes(file):
	bbox=[0,0,0,0]	#minx miny maxx maxy
	bboxes=[]
	with open(file,"r",encoding='utf-8') as osm:
		for ligne in osm: #cherche la déclaration bounds
			if ligne.find("<bounds ")>=0:
				bbox[0]=float(get_tag_value(ligne,"minlon"))
				bbox[2]=float(get_tag_value(ligne,"maxlon"))
				bbox[1]=float(get_tag_value(ligne,"minlat"))
				bbox[3]=float(get_tag_value(ligne,"maxlat"))
				bboxes.append([i for i in bbox])
	if len(bboxes)<1: bboxes.append(get_bbox_from_nodes(file))
	return bboxes
	
def make_tags_string(tag_list):
#["highway=track";"tracktype=grade1"]
#    <tag k='highway' v='primary' />
	l=""
	for t in tag_list:
		kv=t.split('=')
		if len(kv)!=2: 
			print('tag ignoré, mal conditionné en "key=value" : "'+t+'"')
		else: 
#			l+="    <tag k='"+kv[0]+"' v='"+kv[1].replace("_"," ")+"' />\n"
			l+="    <tag k='"+kv[0]+"' v='"+kv[1]+"' />\n"
	return l

def make_tags_string_from_tuple_list(tag_list):
#    <tag k='highway' v='primary' />
	l=""
	for kv in tag_list:
		if kv[1].find("'")>=0: l+='    <tag k="'+kv[0]+'" v="'+kv[1]+'" />\n'
		else: l+="    <tag k='"+kv[0]+"' v='"+kv[1]+"' />\n"
	return l

def distance(lat1,lon1,lat2,lon2):
	"""distance entre les deux points, en mètres """
#	a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2) phi=latitude
#	c = 2 ⋅ atan2( √a, √(1−a) )
#	d = R ⋅ c 	
	a=(math.sin((math.radians(lat2)-math.radians(lat1))/2))**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*((math.sin((math.radians(lon2)-math.radians(lon1))/2))**2)
	d = 6371000 * 2*math.atan2(math.sqrt(a),math.sqrt(1-a))
	return d
	
def travel_ang_dist(lat1,lon1,angle,dist):
	"""dist en mètres, angle horaire depuis le nord en degrés"""
	#φ2 = asin( sin φ1 ⋅ cos δ + cos φ1 ⋅ sin δ ⋅ cos θ )
	#λ2 = λ1 + atan2( sin θ ⋅ sin δ ⋅ cos φ1, cos δ − sin φ1 ⋅ sin φ2 )
	#φ is latitude, λ is longitude, θ is the bearing (clockwise from north), δ is the angular distance d/R; d being the distance travelled, R the earth’s radius
	R=6371000
	delta=dist/R
	lat2=math.degrees(math.asin(math.sin(math.radians(lat1))*math.cos(delta)+math.cos(math.radians(lat1))*math.sin(delta)*math.cos(math.radians(angle))))
	lon2=math.degrees(math.radians(lon1)+math.atan2(math.sin(math.radians(angle))*math.sin(delta)*math.cos(math.radians(lat1)),math.cos(delta)-math.sin(math.radians(lat1))*math.sin(math.radians(lat2))))
	return(lat2,lon2)

def _sign(x):
	if x<0: return -1
	elif x>0: return 1
	else: return 0
def _root(x1,x2,func,error=0.1,max_iter=1000):
#	print(x1,x2,func,error,"\n",func(x1),func(x2))
	if func(x1)*func(x2)>0: raise ValueError("La racine n'est pas encadrée")
	y,z=x1,x2
	i=0
	while abs(func(z))>abs(error):
		i+=1
#		print(i,y,z,func(z))
		y,z=_ridders_get_next(y,z,func)
#		print(i,y,z,func(z))
		if i>max_iter: raise ValueError("Nombre maximal d'itérations atteint")
	return z
def _ridders_get_next(x1,x2,func):
	x3 = (x1+x2)/2
	x4 = x3 + (x3-x1) * (_sign(func(x1)-func(x2))*func(x3)) / math.sqrt((func(x3))**2-func(x1)*func(x2))
	if func(x4)*func(x1)<0: x5=x1
	else: x5=x2
	return (x5,x4)
def offset_meters(lat,lon,dym,dxm):
	nlat=lat+dym*(.1/11000)
	nlat=_root(lat,nlat,lambda x:distance(lat,lon,x,lon)-abs(dym))
	nlon=lon+dxm*(.1/1000)
	nlon=_root(lon,nlon,lambda x:distance(lat,lon,lat,x)-abs(dxm))
	return nlat,nlon

def offset_numvalue(ligne,key,offset):
	debut=ligne.find(key)+len(key)+2
	fin=ligne.find('"',debut+1)
	if fin<0:
		fin=ligne.find("'",debut+1)
#	print(ligne[debut:fin])
	new=float(ligne[debut:fin])+offset
	return ligne[:debut]+str(new)+ligne[fin:]
	
def replace_value(ligne,key,value):
	if get_tag_value(ligne,key)=="": raise ValueError("Key {} not found or empty in string {}".format(key,ligne))
	debut=ligne.find(key+"=")+len(key)+2
	fin=ligne.find('"',debut)
	if fin<0:
		fin=ligne.find("'",debut)
	#print(debut,fin,ligne[debut:fin])
	return ligne[:debut]+value+ligne[fin:]
