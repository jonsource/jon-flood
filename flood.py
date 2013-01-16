import time

SL_NORMAL = 0
SL_NEWYORK = 1
SL_ROOT2 = 2

class Landmap:
    def __init__(self,terr):
        self.terrain = terr
        self.base_terrain = 0
        self.landcosts = []
        self.flooding = []
        self.max_terrain = 20
        self.max_landcosts = 0
        self.max_flooding = 0

    def new_terrain(self,w,h,b=0):
        self.terrain = [w*[b] for i in range(h) ]
        self.base_terrain = b
        
        

    def count_landcosts(self):
        self.landcosts = [len(self.terrain[0])*[0] for i in range(len(self.terrain)) ]
        
        for i in range(0,len(self.terrain)):
            for j in range(0,len(self.terrain[0])):
                for iof in range(-1,2):
                    iin = i+iof
                    if((iin<0) | (iin>=len(self.terrain))):
                        continue
                    for jof in range(-1,2):
                        jin = j+jof
                        if((jin<0) | (jin>=len(self.terrain[0]))):
                            continue
                        if((iof==0) & (jof==0)):
                            self.landcosts[i][j]=self.landcosts[i][j]+self.terrain[iin][jin]
                        else:
                            self.landcosts[i][j]=self.landcosts[i][j]+int(self.terrain[iin][jin]/2)
        self.max_landcosts = self._max_map(self.landcosts)
        return self.landcosts

    def count_flooding_init(self,heuristic=False,slant=SL_NORMAL):
        self.opt_heuristic = heuristic
        self.opt_slant = slant
        self.flooding = [len(self.landcosts[0])*[[-1,0,0]] for i in range(len(self.landcosts)) ]
        self.stack=[]
        self.stack.append([0,0,0,0,0])
        self.start_time=time.clock()

    def count_flooding(self,heuristic=False):
        self.count_flooding_init(heuristic)
        o=1
        while (self.count_flooding_step()>0):
            pass
        return self.flooding

    def _count_flooding_finalize(self):
        if(len(self.stack)==0):
            self.max_flooding = self._max_map(self.flooding)
            self.end_time=time.clock()
            print("time taken :"+repr(self.end_time-self.start_time))
        return len(self.stack)
    
    def count_flooding_step(self):
        if(len(self.stack)<1):
            return 0
        else:
            ind=self.stack.pop()
            i=ind[0]
            j=ind[1]
            cost=ind[2]
            pi=ind[3]
            pj=ind[4]
            if((self.flooding[i][j][0]!=-1) & (self.flooding[i][j][0]<=(self.landcosts[i][j]+cost))):
                return self._count_flooding_finalize()
            self.flooding[i][j]=[self.landcosts[i][j]+cost,pi,pj]
            ca = self.landcosts[i][j]*0.4
            cost = self.flooding[i][j][0]
            for iof in range(-1,2):
                iin = i+iof
                if((iin<0) | (iin>=len(self.terrain))):
                    continue
                for jof in range(-1,2):
                    jin = j+jof
                    cost_add=0
                    if((jin<0) | (jin>=len(self.landcosts[0])) | ((jof==0) & (iof==0))):
                        continue
                    if((jof!=0) & (iof!=0)):
                        if(self.opt_slant == SL_NEWYORK):
                            continue
                        if(self.opt_slant == SL_ROOT2):
                            cost_add=ca
                    if((self.opt_heuristic==True) & (self.flooding[iin][jin][0]!=-1) & (self.flooding[iin][jin][0]<=(self.landcosts[iin][jin]+cost+cost_add))):
                        continue
                    self.stack.append([iin,jin,cost+cost_add,i,j])
        
        return self._count_flooding_finalize()

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

    def reset_landcosts(self):
        self.landcosts=[]
        self.max_landcosts=0

    def reset_flooding(self):
        self.flooding=[]
        self.max_flooding=0

t = [[ 0, 0,],[ 1,0 ],]
lm = Landmap(t)
lm.count_landcosts()
print("costs")
#for row in map2:
#    print(row)

print("flooding")

lm.count_flooding(heuristic=False)
lm.reset_flooding()
lm.count_flooding(heuristic=True)
print("flood")
#for row in map3:
#    print(row)
