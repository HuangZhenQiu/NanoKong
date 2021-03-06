#Sen Zhou 12.8.14 
#define how to parse URLs like EE_Building/3F/ROOM318#near(0,1,2)&inside(3F),  
#(, ), &, |, are preserved key words
#priority | < & < ~
#any kind of spaces, tabs or "\n" are not allowed in URL
import sys, traceback, os

sys.path.append(os.path.join(os.path.dirname(__file__), "./pyparsing"))
from configuration import *
from models import *
from locationTree import *
from pyparsing import *
'''
#BNF Rules:
<Number> ::= [0-9] | [0-9] <Number>
<real> ::= <number> |<number> ',' <number>  
<coordinate> ::= ',' <number> ',' <number> ',' <number> ','
<word> ::= '[a-zA-Z_]' | <word> '[a-zA-Z0-9_]'
<function_name> ::=<word>
<parameter> ::= <word> | <real>
<parameter_list> ::= <parameter> | <parameter_list> ',' <parameter>
<function> = <function_name> '('Optional(<parameter_list>) ')'
<opNegate> = <function> | '~' <opNegate>
<opAnd> = <opNegate> | <opNegate> '&' <opAnd>
<opOr> = <opAnd> | <opOr> '|' <opOr>
<path> = '/' <word> | <path> '/' <word> 
<specification> = <path> | <path>'#' <opOr>
<location_def> = <path>'@'<coordinate>
'''
class LocationParser:
    def __init__(self, locationTree):
        self.nodeIdSet = set([]) 
        self.locationTree = locationTree

    def evaluateAnd(self, locTreeNode, argument):
        print "argument in evalAnd:"+str(argument)
        if len(argument)==1:
            return self.evaluate(locTreeNode, argument[0])
        return self.evaluate(locTreeNode, argument[0]).intersection(self.evaluate(locTreeNode, argument[1]))

    def evaluateOr(self, locTreeNode, argument):
        if len(argument)==1:
            return self.evaluate(locTreeNode, argument[0])
        return self.evaluate(argument[0]).union(self.evaluate(locTreeNode, argument[1]))

    def evaluateNegate(self, locTreeNode, argument):
        return locTreeNode.idSet - self.evaluate(locTreeNode, argument[0])
        
    def evaluateFunction(self, locTreeNode, argument):
        arglst = argument[1:]
        print "function arguments:", argument
        return self._funct_dict[argument[0]](locTreeNode, *arglst)
    
    def parsePath(self):
        def evaluatePath(s, loc, toks):
            locTreeNode =  self.locationTree.findLocation(self.locationTree.root, s)
            return [locTreeNode]
        return evaluatePath
        
    def evaluateSpec(self, locTreeNode, argument):
        print "argument: "+str(argument)
        locTreeNode = argument[0]
        if len(argument)<2:     #if no functions after URL, shortcut for URL#getAll()
            return locTreeNode.getAllAliveNodeIds()
        return self.evaluate(locTreeNode, argument[1])
        
    def evaluate(self, locTreeNode, argument):
        print 'name: '+argument.getName()+" "+str(argument)
        return self._funct_dict[argument.getName()](self, locTreeNode, argument)
        
    #different functions
    
    def isID(locationTreeNode, id):
        id = int(id)
        if id in locationTreeNode.getAllNodes():
            return set([id])
        return set([])
        
    def getAll(locationTreeNode):
        return locationTreeNode.getAllAliveNodeIds()
        
    def near(locationTreeNode, dist, x, y=None,z=None):
        ret_val = set([])
        dist = float(dist)
        obj = None
        try:            #case one, coordinates are given
            x = float(x)
            y = float(y)
            z = float(z)
        except ValueError:  #case 2, the name of a landmark is given, x would be the landmarkName
            landMarks = locationTreeNode.findLandmarksByName(x)
            # Assume we use the first landmark of the same name
            if landMarks ==None or len(landMarks)==0:   #no such landmark of the name
                return ret_val
            x = landMarks[0].coord[0]
            y = landMarks[0].coord[1]
            z = landMarks[0].coord[2]
            obj = landMarks[0]
        idLst = list(locationTreeNode.idSet)
        for sensorId in idLst:
            sensorNd = locationTreeNode.getSensorById(sensorId)
            dist = (sensorNd.coord[0]-x)**2+(sensorNd.coord[1]-y)**2+(sensorNd.coord[2]-z)**2
            if obj!=None:
                dist = self.calcDistance(sensorNd, obj)
            if dist <= dist**2:
                #print sensorNd.coord[0],sensorNd.coord[1],sensorNd.coord[2]
                ret_val.add(sensorNd.nodeInfo.nodeId)
        return ret_val

    #return the closest 'count' nodes from idset(or location treenode is idset=None) to x,y,z(or x)
    def closest(locationTreeNode, x, y=None,z=None, count=-1, idLst=None):
        node_lst = []       #list of nodes to be returned
        dist_lst = []       #list of nodes' distances in the node_list
        obj = None
        try:            #case one, coordinates are given
            x = float(x)
            y = float(y)
            z = float(z)
        except ValueError:  #case 2, the name of a landmark is given, x would be the landmarkName
            landMarks = locationTreeNode.findLandmarksByName(x)
            # Assume we use the first landmark of the same name
            if landMarks ==None or len(landMarks)==0:   #no such landmark of the name
                return ret_val
            x = landMarks[0].coord[0]
            y = landMarks[0].coord[1]
            z = landMarks[0].coord[2]
            obj = landMarks[0]

        if count ==-1:
            count = 65535   #count==-1 means we find and sort all

        largest_dist = 0
        if idLst == None:
            idLst = list(locationTreeNode.idSet)
        for sensorId in idLst:
            sensorNd = locationTreeNode.getSensorById(sensorId)
            if sensorNd == None:
                continue
            
            dist = (sensorNd.coord[0]-x)**2+(sensorNd.coord[1]-y)**2+(sensorNd.coord[2]-z)**2
            if obj!=None:
                dist = self.calcDistance(sensorNd, obj)
            if dist >= largest_dist:
                if len(node_lst)<count:
                    #print sensorNd.coord[0],sensorNd.coord[1],sensorNd.coord[2]
                    node_lst.append(sensorNd.nodeInfo.nodeId)
                    dist_lst.append(dist)
                    largest_dist = dist
            else:
                for i in range(len(node_lst)):
                    if dist_lst[i] > dist:
                        node_lst.insert(i, sensorNd.nodeInfo.nodeId)
                        dist_lst.insert(i, dist)
                        break
        return node_lst

    def farthest(locationTreeNode, x, y=None,z=None, count=-1, idLst=None):
        return LocationParser.__dict__["closest"](locationTreeNode, x, y,z, count, idLst).reverse()
    
    #sort nodes according to their distance to center
    def findCenter(locationTreeNode, count=-1, idLst=None):
        if idLst == None:
            idLst = list(locationTreeNode.idSet)
        sum=(0,0,0)
        for sensorId in idLst:
            sensorNd = locationTreeNode.getSensorById(sensorId)
            sum = (sum[0] + sensorNd.coord[0], 
                   sum[1] + sensorNd.coord[1],
                   sum[2] + sensorNd.coord[2])
        return LocationParser.__dict__["closest"] (locationTreeNode, sum[0], sum[1], sum[2], count, idLst)
        
    def inside(locationTreeNode, landMarkName):
        landMarkLst = locationTreeNode.findLandmarksByName(landMarkName)
        retLst = []
        idLst = list(locationTreeNode.idSet)
        for sensorId in idLst:
            sensorNd = locationTreeNode.getSensorById(sensorId)
            for obj in landMarkLst:
                if (obj.coord[0]-obj.size[0]/2<=landMarkNode.coord[0]<=obj.coord[0]+obj.size[0]/2 and
                    obj.coord[1]-obj.size[1]/2<=landMarkNode.coord[1]<=obj.coord[1]+obj.size[1]/2 and
                    obj.coord[2]-obj.size[2]/2<=landMarkNode.coord[2]<=obj.coord[2]+obj.size[2]/2):
                    retLst.append(sensorId)
                    break
        return set(retLst)
    
    def outside(locationTreeNode, landMarkName):
        return locationTreeNode.idSet - inside(locationTreeNode, landMarkName)
    
    def tangent(locationTreeNode, landMarkName):
        landMarkLst = locationTreeNode.findLandmarksByName(landMarkName)
        retLst = []
        idLst = list(locationTreeNode.idSet)
        for sensorId in idLst:
            sensorNd = locationTreeNode.getSensorById(sensorId)
            coord = sensorNd.coord
            #use checkPoint for tangentcheckPoint<0: no tangent, checkPoint>=1:tangent
            #tangent in one direction:1, within range:0, outside range:-5(continue)
            #error range 1/20 size.
            for obj in landMarkLst:
                checkPoint = 0  
                for i in range(3):
                    if (obj.coord[i]-obj.size[i]*11/20<=coord[i]<=obj.coord[i]+obj.size[i]*9/20 or
                        obj.coord[i]+obj.size[i]*9/20<=coord[i]<=obj.coord[i]+obj.size[i]*11/20):
                        checkPoint = checkPoint + 1
                    elif obj.coord[i]-obj.size[i]/2<= coord[i]<=obj.coord[i]+obj.size[i]/2:
                        scpre = checkPoint + 0
                    else:
                        checkPoint = -5
                        break
                if checkPoint >=1:
                    retLst.append(sensorId)
                    break
        return set(retLst)
    
    #dimension --0 for x, 1 for y, 2 for z, 
    #set dimention to 2 is equivalent to above()
    def front(locationTreeNode, landMarkName, dimension):
        landMarkLst = locationTreeNode.findLandmarksByName(landMarkName)
        retLst = []
        idLst = list(locationTreeNode.idSet)
        for sensorId in idLst:
            sensorNd = locationTreeNode.getSensorById(sensorId)
            for obj in landMarkLst:
                checkPoint = 0
                for i in range(3):
                    if i != dimension:
                        if obj.coord[i]-obj.size[i]/2<=sensorNd.coord[i]<=obj.coord[i]+obj.size[i]/2:
                            checkPoint = checkPoint +1
                        else:
                            break
                    else:
                        if sensorNd.coord[i]>=obj.coord[i]+obj.size[i]/2:
                            checkPoint = checkPoint +1
                        else:
                            break
                print checkPoint, i
                if checkPoint ==3:
                    retLst.append(sensorId)
                    break
        return set(retLst)
    def back(locationTreeNode, landMarkName, dimension):
        landMarkLst = locationTreeNode.findLandmarksByName(landMarkName)
        retLst = []
        idLst = list(locationTreeNode.idSet)
        for sensorId in idLst:
            sensorNd = locationTreeNode.getSensorById(sensorId)
            checkPoint = 0
            for obj in landMarkLst:
                for i in range(3):
                    if i != dimension:
                        if obj.coord[i]-obj.size[i]/2<=landMarkNode.coord[i]<=obj.coord[i]+obj.size[i]/2:
                            checkPoint = checkPoint +1
                        else:
                            break
                    else:
                        if landMarkNode.coord[i]<=obj.coord[i]-obj.size[i]/2:
                            checkPoint = checkPoint +1
                        else:
                            break
                if checkPoint ==3:
                    retLst.append(sensorId)
                    break
        return set(retLst)
    def above(locationTreeNode, landMarkName):
        return LocationParser.__dict__["front"](locationTreeNode, landMarkName, 2)
    def below(locationTreeNode, landMarkName):
        return LocationParser.__dict__["back"](locationTreeNode, landMarkName, 2)
    
    def hasClass(locationTreeNode, classId):
        retLst = []
        for ndInfo in locationTreeNode.getAllNodeInfos():
            if classId in [x.id for x in ndInfo.wuclasses]:
                retLst.append(ndInfo.nodeId)
        return retLst
                
    _funct_dict = {
            u"specification":evaluateSpec,u"function":evaluateFunction,
            u"not":evaluateNegate, u"and":evaluateAnd, u"or": evaluateOr, 
            u"near":near, u"isID":isID, u"getAll":getAll, u"hasClass":hasClass,
            u"inside":inside, u"outside":outside, u"tangent":tangent, 
            u"above":above, u"below":below,u"front":front, u"back":back,
            u"closest": closest, u"farthest":farthest, u"findCenter":findCenter}
            
            
    def _isFuncParameter(self, numStr):
        try:
            numPara = float(numStr)
        except ValueError:
            return False
        return True
    
    def _isFuncName(self, nameStr):
        if self.funct_dict.has_key(nameStr):
            return True
        return False

    def parse(self, str):
        real = Combine( Word(nums) +(u'.' + Word(nums))*(0,1) )
        word = Word( srange(u"[a-zA-Z_]"), srange(u"[a-zA-Z0-9_]") )
        function_name = word
        EQUAL = Literal(u'=').suppress()
        LPAR = Literal(u'(').suppress()
        RPAR = Literal(u')').suppress()
        COMMA = Literal(u',').suppress()
        NOT = Literal(u'~').suppress()
        AND = Literal(u'&').suppress()
        OR  =Literal(u'|').suppress()
        SLASH = Literal(u'/').suppress()
        POND = Literal(u'#').suppress()
        AT = Literal(u'@').suppress()
        parameter = word | real
        parameter_list = parameter + ( COMMA+ parameter )*(None, None)
        function = Group(function_name + LPAR + (parameter_list)*(0,1)+RPAR).setResultsName(u"function")
        coordinate = LPAR + real + (COMMA + real)*2 + RPAR
        opNegate = Forward()        #declaration for recursive definition
        opNegate << (Group(NOT + opNegate).setResultsName(u"not") | function)
        opAnd = Forward()
        opAnd << (Group(opNegate + AND + opAnd).setResultsName(u"and") | Group(opNegate).setResultsName(u"and"))
        opOr = Forward()
        opOr << (Group(opAnd + OR + opOr).setResultsName(u"or") | Group(opAnd).setResultsName(u"or"))
        path = (Group((SLASH + word)*(1, None))).setParseAction(self.parsePath())
        specification = (Group(path + POND + opOr *(0,1))).setResultsName(u"specification") | Group(path).setResultsName(u"specification")
        location_def = path + AT +coordinate   #not used, because this file is for specificaiton parser
        try:
            if str == "" or str == "/":
                str = "/"+ LOCATION_ROOT
            if len(str)>1 and str[0]!='/':
                str = '/'+str
            result =  specification.parseString(str, True)
#            print "parse result: ", result
            return self.evaluate(None, result[0])
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print str
            print traceback.print_exception(exc_type, exc_value, exc_traceback,
                                          limit=2, file=sys.stdout)
            raise

if __name__ == "__main__":
    locTree = LocationTree(u"universal")
    loc0 = u"universal/Boli_Building/3F/South_Corridor/Room318@(3,1,8)"
    loc1 = u"universal/Boli_Building/3F/N_Corridor/Room318@(8,1,3)"
    loc2 = u"universal/Boli_Building/2F/South_Corridor/Room318@(4,4,4)"
    loc3 = u"universal/Boli_Building/3F/South_Corridor/Room318@(2,6,8)"
    senNd0 = SensorNode(Node(0, loc0))
    senNd1 = SensorNode(Node(1, loc1))
    senNd2 = SensorNode(Node(2, loc2))
    senNd3 = SensorNode(Node(3, loc3))
    locTree.addSensor(senNd0)
    locTree.addSensor(senNd1)
    locTree.addSensor(senNd2)
    locTree.addSensor(senNd3)
    landmark1 = LandmarkNode(0, u'door',u"universal/Boli_Building/3F/South_Corridor/Room318@(3,1,9)", (2,1,4))
    landmark2 = LandmarkNode(0, u'window',u"universal/Boli_Building/3F/South_Corridor/Room318@(3,7,5)", (2,2,4))
    locTree.addLandmark(landmark1)
    locTree.addLandmark(landmark2)
    locTree.printTree(locTree.root, 0)
    query = u"/universal/Boli_Building#above(window)"
    query2=u"/universal/Boli_Building#findCenter()"
    func = u"nearest(4,4,4)"
    locParser = LocationParser( locTree)
    result = locParser.parse(query2)
    print "parser result", result
    print [locTree.getNodeInfoById(nodeId) for nodeId in result]
#    print locParser.evaluate(None, locParser.parse(query2)[0])
#   print locURLHandler.locationTreeNode.sensorLst
    loc3 = u"universal/Boli_Building/3F/South_Corridor/Room318#getAll()"
#res = LocationParser.loc_def.parseString(loc3)
#print res
   #
