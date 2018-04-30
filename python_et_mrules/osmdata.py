#-*- coding: utf-8 -*-
#
# Code fourni par JB : http://osm.org/user/JBacc1 ou @RandoCarto (https://twitter.com/RandoCarto) sous licence GPL v3 ou suivantes

from osmxml_routines import *

#class Attribute:
#	def __init__(self,k,v):
#		self._kv=(k,v)
#	def get_k(self):
#		return self._kv[k]
#	def get_v(self):
#		return self._kv[v]
#	def get_kv(self):
#		return self._kv
#
class Attributes:
	def __init__(self, attr_list):
# attr_list:[Attribute1,Attribute2…]
		self._dict= {}
		for kv in attr_list:
			self._dict[kv[0]]=kv[1]
#	def has(self,key):
#		return (key in list(self._dict.keys()))
	def __repr__(self):
		return str(self.list_tags())
	def has(self,k,v=None):
		if k in list(self._dict.keys()):
			if v!=None: return self._dict[k]==v
			else: return True
		else: return False
	def get(self,k):
		return self._dict[k]
	def set_kv(self,k,v):
		self._dict[k]=v
	def get_attributes(self):
		return self._dict
	def list_tags(self):
		t=[]
		for k in list(self._dict.keys()):
			t.append((k,self._dict[k]))
		return t		
	def remove(self,k):
		del self._dict[k]
	def equals(self,attr_2):
		equals=True
		for key in list(self._dict.keys()):
			if not(attr_2.has(key)): equals=False
			elif not(attr_2.has(key,self._dict[key])): equals=False
			if not equals: break	
		for key in list(attr_2._dict.keys()):
			if not(self.has(key)): equals=False
			elif not(self.has(key,attr_2._dict[key])): equals=False
			if not equals: break
		return equals

class Point:
	def __init__(self,x,y):
		self._x=x
		self._y=y
	@property
	def x(self):
		return self._x
	@property
	def y(self):
		return self._y
	@property
	def xy(self):
		return self.x,self.y
	def offset(self,dx,dy):
		self._x+=dx
		self._y+=dy
	def move_to(self,x,y):
		self._x=x
		self._y=y
	def offset_meters(self,dxm,dym):
		self._y,self._x=offset_meters(self.y,self.x,dym,dxm)
	def equals(self,p_2):
		if (self.x!=p_2.x) or (self.y!=p_2.y): return False
		else: return True
	
class OsmObject:
	def __init__(self,id,attr_list,action="",timestamp="",uid="",user="",visible="",version="",changeset=""):
		self._tags=Attributes(attr_list)
		self._id=id
		self.action=action
		self.timestamp=timestamp
		self.uid=uid
		self.user=user
		self.visible=visible
		self.version=version
		self.changeset=changeset
	@property
	def tags(self):
		return self._tags.list_tags()
	@property
	def id(self):
		return self._id
	def has_tag(self,k,v=None):
		return self._tags.has(k,v)
	def set_tag(self,k,v):
		self._tags.set_kv(k,v)
	def get_tag(self,k):
		if self.has_tag(k): return self._tags.get(k)
	def remove_tag(self,k):
		self._tags.remove(k)
		
		
class OsmNode(OsmObject):
	def __init__(self,id,x,y,attr_list,action="",timestamp="",uid="",user="",visible="",version="",changeset=""):
		super(OsmNode,self).__init__(id,attr_list,action,timestamp,uid,user,visible,version,changeset)
		self._location=Point(x,y)
#		self._x=x
#		self._y=y
	def __repr__(self):
		s="node "+str(self.id)+" :"
		s+="("+str(self.location.x)+","+str(self.location.y)+")"
		s+="tags"+str(self.tags)
		return s
	@property
	def location(self):
		return self._location
#	@property
#	def x(self):
#		return self._x
#	@property
#	def y(self):
#		return self._y
	
class OsmWay(OsmObject):
	def __init__(self,id,nodes,attr_list,action="",timestamp="",uid="",user="",visible="",version="",changeset=""):
		super(OsmWay,self).__init__(id,attr_list,action,timestamp,uid,user,visible,version,changeset)
		self._nodes=nodes
		try: self._is_closed=(nodes[0]==nodes[-1])
		except: pass
		self._nodes_count=len(self._nodes)
	@property
	def is_closed(self):
		return self._is_closed
	@property
	def nodes(self):
		return self._nodes
	@property
	def nodes_count(self):
		return self._nodes_count

class OsmReferenceType():
	NODE="node"
	WAY="way"
	RELATION="relation"
	
class OsmRelationMember():
	def __init__(self,ref_id,ref_type,role):
		self._ref_id=ref_id
		self._ref_type=ref_type
		self._role=role
	@property
	def ref_id(self):
		return self._ref_id
	@property
	def ref_type(self):
		return self._ref_type
	@property
	def role(self):
		return self._role

class OsmRelation(OsmObject):
	def __init__(self,id,members,attr_list,action="",timestamp="",uid="",user="",visible="",version="",changeset=""):
		super(OsmRelation,self).__init__(id,attr_list,action,timestamp,uid,user,visible,version,changeset)
		self._members=members
	@property
	def members(self):
		return self._members
		
class Bbox():
	def __init__(self,t):
		[minx,miny,maxx,maxy]=t
		self.minx=minx
		self.miny=miny
		self.maxx=maxx
		self.maxy=maxy
		self.bbox=(minx,miny,maxx,maxy)	
class Bboxes():
	def __init__(self,bbxs):
		self._bboxes=[]
		for bb in bbxs:
			self._bboxes.append(Bbox(bb))
	@property
	def bboxes(self):
		return self._bboxes
		
def make_detail(action,timestamp,uid,user,visible,version,changeset):
	l=""
	if action!="": l+="action='"+action+"' "
	if timestamp!="": l+="timestamp='"+timestamp+"' "
	if uid!="": l+="uid='"+uid+"' "
	if user!="": l+="user='"+user+"' "
	if visible!="": l+="visible='"+visible+"' "
	if version!="": l+="version='"+version+"' "
	if changeset!="": l+="changeset='"+changeset+"' "
	return l
	
class OsmData(Bboxes):
	def __init__(self):
		super(OsmData,self).__init__([])
		self.upload="false"
		self._nodes={}
		self._ways={}
		self._relations={}
		self._new_id=-1
	
	def add_node(self,node):
		self._nodes[node.id]=node
	def add_way(self,way):
		self._ways[way.id]=way
	def add_relation(self,rel):
		self._relations[rel.id]=rel
	def make_new_id(self):
		self._new_id-=1
		return self._new_id
		
	@property
	def nodes(self):
		return self._nodes
	@property
	def ways(self):
		return self._ways
	@property
	def relations(self):
		return self._relations
	
	def node(self,id):
		return self._nodes[id]
	def way(self,id):
		return self._ways[id]
	def relation(self,id):
		return self._relations[id]
	
	def has_node(self,id):
		if id in list(self._nodes.keys()): return True
		else: return False
	def has_way(self,id):
		if id in list(self._ways.keys()): return True
		else: return False
	def has_relation(self,id):
		if id in list(self._relations.keys()): return True
		else: return False
	
	def load_xml_file(self,file,keep_detail=True,drop_deleted=True):
		super().__init__(get_bboxes(file))
		with open(file,'r',encoding='utf-8') as xml:
			obj,id="",-1
			action,timestamp,uid,user,visible,version,changeset="","","","","","",""
			for ligne in xml:
				if is_upload(ligne): self.upload=str(get_upload(ligne)).lower()##$$ voir pour utiliser get_tag_value
				
				if get_object_type(ligne)!="": 
					obj=get_object_type(ligne)
					id=get_object_id(ligne)
					tags=[]
					nds=[]
					members=[]
					if obj=="node":
						lat,lon=get_node_lat_lon(ligne)
						x,y=lon,lat
					if keep_detail:#action="",timestamp="",uid="",user="",visible="",version="",changeset=""
						action=get_tag_value(ligne,"action")
						timestamp=get_tag_value(ligne,"timestamp")
						uid=get_tag_value(ligne,"uid")
						user=get_tag_value(ligne,"user")
						visible=get_tag_value(ligne,"visible")
						version=get_tag_value(ligne,"version")
						changeset=get_tag_value(ligne,"changeset")
						
				if get_node_ref(ligne)!=0:
					nds.append(get_node_ref(ligne))
				if get_member(ligne)!=0:
					mmb=get_member(ligne)
					members.append(OsmRelationMember(mmb[0],mmb[1],mmb[2]))			
				
				if is_tag(ligne):
					kv=get_kv(ligne)
					tags.append(kv)
				
				if is_object_end(ligne) and obj!="" and (not(drop_deleted and action=="delete")):
					if obj=="node":
						node=OsmNode(id,x,y,tags,action,timestamp,uid,user,visible,version,changeset)
						self.add_node(node)
					if obj=="way":
						way=OsmWay(id,nds,tags,action,timestamp,uid,user,visible,version,changeset)
						self.add_way(way)
					if obj=="rel":
						rel=OsmRelation(id,members,tags,action,timestamp,uid,user,visible,version,changeset)
						self.add_relation(rel)
		self._new_id=min(min(list(self.nodes.keys())+[0]),min(list(self.ways.keys())+[0]),min(list(self.relations.keys())+[0]))-1
	
	def save_xml_file(self,file,keep_detail=True):
		with open(file,'w',encoding='utf-8') as xml:
			xml.write("<?xml version='1.0' encoding='UTF-8'?>\n")
			xml.write("<osm version='0.6' upload='"+str(self.upload).lower()+"' generator='Python_script osmdata.py'>\n")
			for bb in self.bboxes:
				xml.write("  <bounds minlat='"+str(bb.miny)+"' minlon='"+str(bb.minx)+"' maxlat='"+str(bb.maxy)+"' maxlon='"+str(bb.maxx)+"'/>\n")

			for id in sorted(self._nodes.keys()):
				node=self._nodes[id]
				ligne="  <node id='"+str(node.id)+"' lat='"+str(node.location.y)+"' lon='"+str(node.location.x)+"' "
				if keep_detail:
					ligne+=make_detail(node.action,node.timestamp,node.uid,node.user,node.visible,node.version,node.changeset)
				if len(node.tags)>0:
					ligne+=">\n"
					ligne+=make_tags_string_from_tuple_list(node.tags)
					ligne+="  </node>\n"
				else: ligne+="/>\n"
				xml.write(ligne)
			for id in sorted(self._ways.keys()):
				way=self._ways[id]
				ligne="  <way id='"+str(way.id)+"' "
				if keep_detail:
					ligne+=make_detail(way.action,way.timestamp,way.uid,way.user,way.visible,way.version,way.changeset)
				ligne+=">\n"
				xml.write(ligne)
				for node_id in way.nodes:
					xml.write("    <nd ref='"+str(node_id)+"' />\n")
				xml.write(make_tags_string_from_tuple_list(way.tags))
				xml.write("  </way>\n")
			for id in sorted(self._relations.keys()):
				relation=self._relations[id]
				ligne="  <relation id='"+str(relation.id)+"' "
				if keep_detail:
					ligne+=make_detail(relation.action,relation.timestamp,relation.uid,relation.user,relation.visible,relation.version,relation.changeset)
				ligne+=">\n"
				xml.write(ligne)
				for member in relation.members:
					xml.write("    <member type='"+member.ref_type+"' ref='"+str(member.ref_id)+"' role='"+member.role+"' />\n")
				xml.write(make_tags_string_from_tuple_list(relation.tags))
				xml.write("  </relation>\n")
			xml.write("</osm>\n")
	
	def find_nodes(self,predicate):
		n=[]
		for node_id in list(self.nodes.keys()):
			if predicate(self.nodes[node_id]): n.append(self.nodes[node_id])
		return n
	def find_ways(self,predicate):
		w=[]
		for way_id in list(self.ways.keys()):
			if predicate(self.ways[way_id]): w.append(self.ways[way_id])
		return w
	def find_relations(self,predicate):
		r=[]
		for relation_id in list(self.relations.keys()):
			if predicate(self.relations[relation_id]): r.append(self.relations[relation_id])
		return r
	
	def remove_way(self,way_id):
		del self._ways[way_id]

#	def _find_object(self,predicate,object_type):
#		if object_type=="node": objects=self.nodes
#		elif object_type=="way": objects=self.ways
#		elif object_type=="relation": objects=self.relations
#		else: raise ValueError("Type d'objet inconnu : {}".format(object_type))
#		obj_out=[]
#		for obj_id in list(objects.keys()):
#			if predicate(objects[obj_id]): obj_out.append(objects[obj_id])
#		return obj_out
