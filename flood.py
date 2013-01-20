import time

# constant definitions
SL_NORMAL = 0
SL_NEWYORK = 1
SL_ROOT2 = 2
NEIGHBORS = ( (-1,-1),(-1,0),(-1,1),
              (0,-1),(0,1),
              (1,-1),(1,0),(1,1) )

# Class storing data about terrain and computed landcosts and pathing
class Landmap:
    def __init__(self,terr=[]):
        self.terrain = terr
        self.base_terrain = 0
        self.landcosts = []
        self.flooding = []
        self.max_terrain = 20
        self.max_landcosts = 0
        self.max_flooding = 0
        self.opt_flood_mode = None
        self.tile_cost_fun = self._count_tile_cost
        

# Create new terrain and reset computed values
    def new_terrain(self,w,h,b=0):
        self.terrain = [w*[b] for i in range(h) ]
        self.base_terrain = b
        self.reset_landcosts()
        self.reset_flooding()

# default function returning neighbors of tile
# include = True: includes the tile itself
# include = False: doesn't include the tile itself, only the surrounding tiles
    def _neighbors(include=True):
        if include :
            return NEIGHBORS+((0,0),)
        return NEIGHBORS

# default function counting landcost value of a tile
    def _count_tile_cost(self,i,j,neigh=_neighbors):
        for iof, jof in neigh():
            iin = i+iof
            if((iin<0) | (iin>=len(self.terrain))):
                continue
            jin = j+jof
            if((jin<0) | (jin>=len(self.terrain[0]))):
                continue
            if((iof==0) & (jof==0)):
                self.landcosts[i][j]=self.landcosts[i][j]+self.terrain[iin][jin]
            else:
                self.landcosts[i][j]=self.landcosts[i][j]+int(self.terrain[iin][jin]/2)


# count landcosts        
    def count_landcosts(self):
        self.landcosts = [len(self.terrain[0])*[0] for i in range(len(self.terrain)) ]
        
        for i in range(0,len(self.terrain)):
            for j in range(0,len(self.terrain[0])):
                self.tile_cost_fun(i,j) #tile_cost_fun is a 
        self.max_landcosts = self._max_map(self.landcosts)
        return self.landcosts

# initialize flooding - used when flooding by iteration
# starts time measuring by setting start_time
    def count_flooding_init(self,heuristic=False,fl_mode=SL_ROOT2):
        self.opt_heuristic = heuristic
        self.opt_flood_mode = fl_mode
        self.flooding = [len(self.landcosts[0])*[[-1,0,0]] for i in range(len(self.landcosts)) ]
        self.mark = [len(self.landcosts[0])*[False] for i in range(len(self.landcosts)) ]
        self.stack=[]
        self.stack.append([0,0,0,0,0])
        self.start_time=time.clock()

# count flooding in one step
    def count_flooding(self,heuristic=True,fl_mode=SL_ROOT2):
        self.count_flooding_init(heuristic,fl_mode)
 
        while (self.count_flooding_step()>0):
            pass
        self._count_flooding_finalize()
        return self.flooding

# finalize the flooding - used when flooding by iteration
# also sets the end_time
    def _count_flooding_finalize(self):
        self.max_flooding = self._max_map(self.flooding)
        self.end_time=time.clock()
        print("time taken :"+repr(self.end_time-self.start_time))
        

    def _count_tile_flood(self,i,j,cost,pi,pj,neigh=_neighbors):
        #print(i,j,cost,pi,pj,neigh)
        self.mark[i][j]=False
        if((self.flooding[i][j][0]!=-1) & (self.flooding[i][j][0]<=(self.landcosts[i][j]+cost))):
            return len(self.stack)
        self.flooding[i][j]=[self.landcosts[i][j]+cost,pi,pj]
        #print("cost1",cost)
        cost = self.flooding[i][j][0]
        #print("cost2",cost)
        # look through neighbors
        for iof,jof in neigh(False):
            iin = i+iof
            if((iin<0) | (iin>=len(self.terrain))):
                continue
            jin = j+jof
            if((jin<0) | (jin>=len(self.terrain[0]))):
                continue
            cost_add=0
            if((jof!=0) & (iof!=0)): # diagonal neighbor
                if(self.opt_flood_mode == SL_NEWYORK):
                    continue
                if(self.opt_flood_mode == SL_ROOT2):
                    cost_add=self.landcosts[iin][jin]*0.4
            if((self.opt_heuristic==True) & (self.flooding[iin][jin][0]!=-1) & (self.flooding[iin][jin][0]<=(self.landcosts[iin][jin]+cost+cost_add))):
                continue
            if(self.mark[iin][jin]==False):
                self.stack.append([iin,jin,cost+cost_add,i,j])
                self.mark[iin][jin]=True
        return len(self.stack)
                
# count next step of flooding - used when flooding by iteration    
    def count_flooding_step(self):
        if(len(self.stack)<1):
            return 0
        else:
            #s = ""
            #for rec in self.stack:
            #    s=s+"["+repr(rec[0])+","+repr(rec[1])+"],"
            #print(s)
            ind=self.stack.pop()
            i=ind[0]
            j=ind[1]
            cost=ind[2]
            pi=ind[3]
            pj=ind[4]
            return self._count_tile_flood(i,j,cost,pi,pj)

# return maximum value of array
    def _max_map(self,mapa):
        ret=0
        for row in mapa:
            for el in row:
                try:
                    if(el[0]>ret):
                        ret=el[0]
                except:
                    if(el>ret):
                        ret=el
        return ret

# resets landcosts computed values
    def reset_landcosts(self):
        self.landcosts=[]
        self.max_landcosts=0

# resets flooding computed values
    def reset_flooding(self):
        self.flooding=[]
        self.max_flooding=0

# test function
    def test(self):
        t = [[ 1, 2,],[ 1,1 ],]
        lm = Landmap(t)
        lm.count_landcosts()
        print("costs")
        for row in lm.landcosts:
            print(row)

        print("flooding")

        lm.count_flooding(heuristic=False)
        lm.reset_flooding()
        lm.count_flooding(heuristic=True)
        print("flood")
        for row in lm.flooding:
            print(row)

    def pr(self):
        print("wow")

l=Landmap()
l.test()
