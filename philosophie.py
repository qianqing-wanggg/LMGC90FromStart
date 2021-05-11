import numpy
import math

from pylmgc90.pre import *

dim = 2

# disk creation
radius = 0.1
disk = avatar(dimension=dim)
disk.addNode( node(coor=numpy.array([0.,0.1]),number=1) )
disk.addBulk( rigid2d() )
disk.defineGroups()
disk.addContactors(shape='DISKx',color='BLUEx',byrd=radius)

# foundation creation
floor = avatar(dimension=dim)
floor.addNode( node(coor=numpy.array([0.,-0.05]),number=1) )
floor.addBulk( rigid2d() )
floor.defineGroups()
floor.addContactors(shape='JONCx',color='BLUEx',axe1=1.,axe2=0.05)


# materials, model and groups definition
mat = material(name='TDURx',materialType='RIGID',density=1000.)
mut = material(name='MOUxx',materialType='RIGID',density=100.)
mod = model(name='rigid', physics='MECAx', element='Rxx2D', dimension=dim)
disk.defineModel(model=mod)
disk.defineMaterial(material=mut)
disk.computeRigidProperties()
floor.defineModel(model=mod)
floor.defineMaterial(material=mat)
floor.computeRigidProperties()

# boundary condition
floor.imposeDrivenDof(component=[1,2,3],dofty='vlocy')

# column creation
import copy
nb_disks = 10
column = avatars()
for i in range(nb_disks):
  new_disk = copy.deepcopy(disk)
  new_disk.translate(dy=i*2.*radius)
  column.addAvatar(new_disk)

# copy column
bodies = avatars()
nb_columns = 3
for i in range(nb_columns):
  new_columns = copy.deepcopy(column)
  new_columns.translate(dx=i*2.*radius)
  for body in new_columns:
    bodies.addAvatar(body)

# adding floor and rotation sample
bodies.addAvatar(floor)

bodies.rotate(description='axis', alpha=-math.pi/6., axis=[0., 0., 1.], center=[1.,-0.05])

try:
  visuAvatars(bodies)
except:
  pass

# containers definitions:
mats = materials()
mats.addMaterial(mat,mut)
svs   = see_tables()
tacts = tact_behavs()

# interaction definition:
ldkjc=tact_behav(name='iqsc0', law='IQS_CLB', fric=0.3)
tacts+=ldkjc
svdkjc = see_table(CorpsCandidat='RBDY2', candidat='DISKx', colorCandidat='BLUEx', behav=ldkjc,
                   CorpsAntagoniste='RBDY2', antagoniste='JONCx', colorAntagoniste='BLUEx', alert=.1)
svs+=svdkjc
svdkdk = see_table(CorpsCandidat='RBDY2', candidat='DISKx', colorCandidat='BLUEx', behav=ldkjc,
                   CorpsAntagoniste='RBDY2', antagoniste='DISKx', colorAntagoniste='BLUEx', alert=.1)
svs+=svdkdk

# files writing
if not os.path.isdir('./DATBOX'):
  os.mkdir('./DATBOX')

writeBodies(bodies,chemin='DATBOX/')
writeBulkBehav(mats,chemin='DATBOX/')
writeTactBehav(tacts,svs,chemin='DATBOX/')
writeDrvDof(bodies,chemin='DATBOX/')
writeDofIni(bodies,chemin='DATBOX/')
writeVlocRlocIni(chemin='DATBOX/')

post = postpro_commands()
writePostpro(commands=post, parts=bodies, path='DATBOX/')

