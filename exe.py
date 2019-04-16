from obj import *
from math import *
from tqdm import *
import webbrowser
import copy
from collections import namedtuple
x = 0.1
y = 0.1
width = 800
height = 600
V2 = namedtuple('Vertex2', ['x', 'y'])
V3 = namedtuple('Vertex3', ['x', 'y', 'z'])
zbuffer = [[-99999999999 for x in range(width+1)] for y in range(height+1)]

def loadModelMatrix(transalte, scale, rotate):
	transalte = V3(*transalte)
	scale = V3(*scale)
	rotate = V3(*rotate)
	translate_matrix=[
		[1,0,0,transalte.x],
		[0,1,0,transalte.y],
		[0,0,1,transalte.z],
		[0,0,0,1]
		]
	scale_matrix = [
			[scale.x,0,0,0],
			[0,scale.y,0,0],
			[0,0,1,scale.z],
			[0,0,0,1]
		]

	a = rotate.x
	rotation_matrix_x =[
			[1,0,0,0],
			[0,cos(a),-sin(a),0],
			[0,sin(a),cos(a),0],
			[0,0,0,1]
		]

	a = rotate.y
	rotation_matrix_y =[
			[cos(a),0,-sin(a),0],
			[0,1,0,0],
			[-sin(a),0,cos(a),0],
			[0,0,0,1]
		]

	a = rotate.z
	rotation_matrix_z =[
			[cos(a),-sin(a),0,0],
			[sin(a),cos(a),0,0],
			[0,0,1,0],
			[0,0,0,1]
		]
	
	rotation_matrix =  mulmat(rotation_matrix_z,mulmat(rotation_matrix_y,rotation_matrix_x))
	
	model = mulmat(scale_matrix,mulmat(rotation_matrix,translate_matrix))
	return model


class Render (object):
	def __init__(self,filename,material = None):
		with open(filename) as f:
			self.lines = f.read().splitlines()

		with open(material) as f:
			self.linesmtl = f.read().splitlines()

		self.tvertices= []
		self.vertices = []
		self.faces = []
		self.material = {}
		self.normales = []

	def read(self):
		materialA = ''
		
		for line in tqdm(self.lines):
			if line:
				prefix, value = line.split(' ',1)

				if prefix == 'v':
					self.vertices.append(list(map(float,value.split(' '))))
				if prefix == 'vt':
					self.tvertices.append(list(map(float,value.split(' '))))
				if prefix == 'vn':
					self.normales.append(list(map(float,value.split(' '))))
				if prefix == 'f':
					
					listf1 = value.split(' ')
					listx = []
					
					for face in listf1:
						listf2 = face.split('/')
						listf = []
						for t2 in listf2:
							if t2:
								listf.append(int(t2))
							else:
								listf.append(0)
								
						listf.append(materialA)
						listx.append(listf)
						self.faces.append(listx)
						
				elif prefix == 'usemtl':
					materialA = value

	def readMtl(self):
		nameMat = ''
		for line in self.linesmtl:
			if line:
				prefix, value = line.split(' ',1)
				if prefix == 'newmtl':
					nameMat = value
				elif prefix == 'Kd':
					coloresStr = value. split(' ')
					listColores = list(map(float,coloresStr))
					self.material[nameMat] = listColores

	def getverts(self):
		return self.vertices
	def getfaces(self):
		return self.faces
	def getmateriales(self):
		return self.material
	def gettverts(self):
		return self.tvertices
	def getnormales(self):
		return self.normales
		
verts = []

def reverse(var):
	varc = []
	vat = []
	for y in range(0,len(var[0])):
		varf = []
		for x in range(0,len(var)):
			if y == 0 :
				vat.append(1)
			varf.append(var[x][y])

		varc.append(varf)

	varc.append(vat)
	return varc

def recover(mat):
    matriz = []
    for y in range(0,len(mat[0])):
        vam = []
        for x in range(0,len(mat)-1):
            vam.append(mat[x][y]/mat[3][y])
        matriz.append(vam)
    return matriz


def mulmat(mat1, mat2):
	mat3 = copy.deepcopy(mat2)
	for y in range(0,len(mat2)):
		for x in range(0,len(mat2[0])):
			mat3[y][x] = fabs(mat3[y][x]*0.0)

	for i in range(0,len(mat1)):
		for j in range(0,len(mat2[1])):
			for k in range(0,len(mat2)):
				mat3[i][j] += mat1[i][k] * mat2[k][j]
				
	return mat3

def loadViewMatrix(x,y,z, center):
	M = [
		[x.x, x.y, x.z, 0],
		[y.x, y.y, y.z, 0],
		[z.x, z.y, z.z, 0],
		[0,0,0,1]
		]
	O = [
		[1,0,0,-center.x],
		[0,1,0,-center.y],
		[0,0,1,-center.z],
		[0,0,0,1]
		]
	
	view = mulmat(O,M)
	
	return view

def loadProjectionMatrix(coeff):
	Projection = [
		[1,0,0,0],
		[0,1,0,0],
		[0,0,1,0],
		[0,0,coeff,1]
	]
	return Projection

def draw():
	verts_itter = iter(verts)
	try:
		while True:
			a = next(verts_itter)
			b = next(verts_itter)
			c = next(verts_itter)
			r.line_float(a[0],a[1],b[0],b[1])
			r.line_float(b[0],b[1],c[0],c[1])
			r.line_float(c[0],c[1],a[0],a[1])
	except StopIteration as e:
		print("f")

def loadViewportMatrix():
	Viewport = [
		[width/500,0,0,x+width/500],
		[0,height/500,0,y + height/500],
		[0,0,16,16],
		[0,0,0,1]
		]
	return Viewport
	
def load(filename,filenameMtl,eye,center,up,transalte, scale, rotate, textura = None):
	model = Render(filename,filenameMtl)
	print("\n Reading model: ", filename)
	model.read()
	model.readMtl()
	tvertices = model.gettverts()
	vertices = model.getverts()
	faces = model.getfaces()
	materiales = model.getmateriales()
	normals = model.getnormales()
	z = normVec(restVec(eye, center))
	x = normVec(prodx(up,z))
	y = normVec(prodx(z,x))
	vert_buff_object = []
	
	 
	matriz = mulmat(loadViewportMatrix(),mulmat(loadProjectionMatrix(-0.1),mulmat(loadViewMatrix(x,y,z, center),loadModelMatrix(transalte, scale, rotate))))
	vertices = mulmat(matriz,reverse(vertices))
	vertices = recover(vertices)
	
	scal = 0.8


	luz=V3(-0.5,1,1)
	for face in faces:
	
		x1=round(scal*(vertices[face[0][0]-1][0]+1)*(getwidth()/2))
		y1=round(scal*(vertices[face[0][0]-1][1]+1)*(getwidth()/2))
		z1=round(scal*(vertices[face[0][0]-1][2]+1)*(getwidth()/2))
		x2=round(scal*(vertices[face[1][0]-1][0]+1)*(getwidth()/2))
		y2=round(scal*(vertices[face[1][0]-1][1]+1)*(getwidth()/2))
		z2=round(scal*(vertices[face[1][0]-1][2]+1)*(getwidth()/2))
		x3=round(scal*(vertices[face[2][0]-1][0]+1)*(getwidth()/2))
		y3=round(scal*(vertices[face[2][0]-1][1]+1)*(getwidth()/2))
		z3=round(scal*(vertices[face[2][0]-1][2]+1)*(getwidth()/2))
		v1 = V3(x1,y1,z1)
		v2 = V3(x2,y2,z2)
		v3 = V3(x3,y3,z3)
		
		normal = normVec(prodx(restVec(v2,v1),restVec(v3,v1)))
		intens = prod(normal,luz)

		if not textura:
			if intens<0:
				pass
			else:
				glColor(materiales[face[0][3]][0]*intens,materiales[face[0][3]][1]*intens,materiales[face[0][3]][2]*intens)

				triangleM(v1,v2,v3)
		else:
			xe1 = int(textura.width * ((tvertices[face[0][1] - 1][0]))) - 1
			ye1 = int(textura.height * ((tvertices[face[0][1] - 1][1]))) - 1
			xe2 = int(textura.width * ((tvertices[face[1][1] - 1][0]))) - 1
			ye2 = int(textura.height * ((tvertices[face[1][1] - 1][1]))) - 1
			xe3 = int(textura.width * ((tvertices[face[2][1] - 1][0]))) - 1
			ye3 = int(textura.height * ((tvertices[face[2][1] - 1][1]))) - 1
			
			t1 = V3(xe1, ye1, 0)
			t2 = V3(xe2, ye2, 0)
			t3 = V3(xe3, ye3, 0)


			for facepart in face:
				norma = V3(*normals[facepart[2]-1])
				vert_buff_object.append(norma)

			n1 = vert_buff_object[0]
			n2 = vert_buff_object[1]
			n3 = vert_buff_object[2]
			vert_buff_object = []
			triangleT(v1,v2,v3,t1,t2,t3,n1,n2,n3,luz,textura,intens)

def barycentric(A, B, C, P):
	cx, cy, cz = prodx(
		V3(B.x - A.x, C.x - A.x, A.x - P.x),
		V3(B.y - A.y, C.y - A.y, A.y - P.y)
	)

	if cz == 0:
		return -1, -1, -1
	u = cx/cz
	v = cy/cz
	w = 1 - (u + v)

	return w,v,u

def bbox(A, B, C):
	xs = sorted([A.x, B.x, C.x])
	ys = sorted([A.y, B.y, C.y])
	return V2(xs[0], ys[0]), V2(xs[2], ys[2])

def triangleM(A, B, C):
	bbox_min, bbox_max = bbox(A, B, C)

	for x in range(bbox_min.x, bbox_max.x + 1):
		for y in range(bbox_min.y, bbox_max.y + 1):
			w, v, u = barycentric(A, B, C, V2(x, y))
			
			if w < 0 or v < 0 or u < 0:
				pass
			else:
				z = A.z * w + B.z * v + C.z * u
				
				try:
					if z > zbuffer[x][y]:
						pointf(x, y)
						zbuffer[x][y] = z
				except:
						pass

def triangleT(A, B, C,tacord, tbcord, tccord, norm1,norm2,norm3,light, texture = None, intense = 1):
	bbox_min, bbox_max = bbox(A, B, C)


	for x in range(bbox_min.x, bbox_max.x + 1):
		for y in range(bbox_min.y, bbox_max.y + 1):
			w, v, u = barycentric(A, B, C, V2(x, y))
			
			if w < 0 or v < 0 or u < 0:
				pass
			else:
				if texture:
					TA,TB,TC = tacord,tbcord,tccord
					tx = TA.x*w + TB.x *v + TC.x *u
					ty = TA.y*w + TB.y *v + TC.y *u
				
				nA = norm1
				nB = norm2
				nC = norm3	
				color = gourad(
					light,
					texture,
					bar = (w,v,u),
					texture_coords = (tx,ty),
					varying_normals = (nA,nB,nC)
					)
				
					
				z = A.z * w + B.z * v + C.z * u
				
				if x<width and x>0 and y<height and y>0 and z > zbuffer[y][x]:
					pointsf(x, y,color)
					zbuffer[y][x] = z
							

def prod(v0,v1):
	return (v0.x*v1.x)+(v0.y*v1.y)+(v0.z*v1.z)
def restVec(v0,v1):
	return V3(v0.x-v1.x,v0.y-v1.y,v0.z-v1.z)
def prodx(v0,v1):
	return V3(
	v0.y * v1.z - v0.z * v1.y,
	v0.z * v1.x - v0.x * v1.z,
	v0.x * v1.y - v0.y * v1.x
		)
def magVec(v0):
	return (v0.x**2 + v0.y**2 + v0.z**2)**0.5
def normVec(v0):
	l = magVec(v0)
	if not l:
		return V3(0, 0, 0)
	return V3(v0.x/l, v0.y/l, v0.z/l)

def gourad(light, texture, **kwargs):
	w,v,u = kwargs['bar']

	tx,ty = kwargs['texture_coords']

	nA,nB,nC = kwargs['varying_normals']

	tcolor = texture.get_colors(tx,ty)

	nx = nA.x * w + nB.x * u + nC.x * v
	ny = nA.y * w + nB.y * u + nC.y * v
	nz = nA.z * w + nB.z * u + nC.z * v

	vn = V3(nx,ny,nz)

	intensity = prod(vn, light)

	return color(
		int(tcolor[2]* intensity) if tcolor[2] * intensity > 0 else 0,
		int(tcolor[1]* intensity) if tcolor[1] * intensity > 0 else 0,
		int(tcolor[0]* intensity) if tcolor[0] * intensity > 0 else 0
		)



glCreateWindow(width,height)

r = get_var()
r.clear()

talduin = Texture("alduin.bmp")
tarmor = Texture("armor.bmp")
tbody = Texture("body.bmp")
tboots = Texture("boots.bmp")
tfloor = Texture("floor.bmp")
tgloves = Texture("gloves.bmp")
thair = Texture("hair.bmp")
thead = Texture("head.bmp")
thelmet = Texture("helmet.bmp")
tshield = Texture("shield.bmp")
tsword = Texture("nedstark.bmp")
tbackground = Texture("SVN.bmp")

bg(tbackground)

eye=V3(0,0,5)
center=V3(-1,-1,-1)
up=V3(0,1,0)
transalte=(-15,-11.1,-4)
scale=(0.625,0.625,0.625)
rotate=(-0.3,-1,-0.1)

#modelo 1
load("helm.obj", "helm.mtl", eye, center, up, transalte, scale, rotate, thelmet)
#modelo 2
load("sword.obj", "sword.mtl", eye, center, up, transalte, scale, rotate, tsword)
#modelo 3
load("alduin.obj", "alduin.mtl", eye, center, up, transalte, scale, rotate, talduin)
#modelo 4
load("shield.obj", "shield.mtl", eye, center, up, transalte, scale, rotate)
#modelo 5
load("dbody.obj", "dbody.mtl", eye, center, up, transalte, scale, rotate, tbody)
load("boots.obj", "boots.mtl", eye, center, up, transalte, scale, rotate, tboots)
load("shoulder.obj", "shoulder.mtl", eye, center, up, transalte, scale, rotate, tbody)
load("gloves.obj","gloves.mtl", eye, center, up, transalte, scale, rotate, tgloves)
load("darms.obj", "darms.mtl", eye, center, up, transalte, scale, rotate, tbody)
load("dhead.obj", "dhead.mtl", eye, center, up, transalte, scale, rotate, thead)
load("dhair1.obj", "dhair1.mtl", eye, center, up, transalte, scale, rotate, thair)
load("dhair2.obj", "dhair2.mtl", eye, center, up, transalte, scale, rotate, thair)

glFinish()
print('done')
print("\n\n")
webbrowser.open("https://www.youtube.com/watch?v=JSRtYpNRoN0")
print("\n\n El viaje ha finalizado, el Dovahkiin (Sangre de Dragon) ha llegado a su ultimo destino: Sovngarde, el mas alla, para finalmente derrotar a Alduin, el Devorador de Mundos. Y con ello poder restablecer la paz en Skyrim y librar a toda Tamriel y Nirn de la destruccion. Solo el puede detener a este legendario ser que alguna vez se creyo derrotado, pero volvio con mas fuerza. Ahora debe de enfrentar a Alduin como ultima tarea que le ha preparado su destino. Pero, lo que no sabe es que esta ultima pelea es la mas dificil, y solo uno saldra victorioso. Para asegurar la victoria, el Dovahkiin tendra que usar toda su fuerza y todo su poder que los dioses le han otorgado para ser el Sangre de Dragon.")
print("\n\n Fus Ro Dah!\n\n")