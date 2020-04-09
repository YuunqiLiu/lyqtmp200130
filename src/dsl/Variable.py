import math,re
from functools  import reduce
from operator   import concat
from copy       import copy

#from .Num       import UInt
from .Root      import Root
from .Value     import Value
import string

class Variable(Root):

    def __init__(self):
        super(Variable,self).__init__()

    @property
    def name_until_component(self):
        return self.name_until_not(Variable)

    @property
    def name_before_component(self):
        return self.name_before_not(Variable)
            
    def __gt__(self,other):
        if not isinstance(other,Variable):
            raise TypeError('%s should compare with a Variable,but get a %s' %(type(self),type(other)))
        elif self.name == other.name:
            raise Exception()
        elif self.name > other.name:
            return True
        else:
            return False

    def __lt__(self,other):
        return not self.__gt__(other)


class SingleVar(Variable,Value):

    def __init__(self,template):#=UInt(1,0)):
        super(SingleVar,self).__init__()
        self.__template = template
        # self.__width = width

    @property
    def width(self):
        return self.__template.width
        # return self.__width

    @property
    def string(self):
        return self.name_before_component #self.__name

    @property
    def lstring(self):
        return self.name_before_component #self.__name

    @property
    def rstring(self):
        return self.name_before_component #self.__name



    @property
    def attribute(self):
        return self.__template
        # return self.__width





class WireSig(SingleVar):
    pass


class Reg(SingleVar):
    pass


class Wire(WireSig):

    #=============================================================================================
    # RTL gen 
    #=============================================================================================

    # @property
    # def verilog_inst(self):
    #     '''生成端口实例化的RTL'''
    #     return [".%s(%s)" %(self.name_before(Component),self.name_until(Component))]

    @property
    def verilog_def(self):
        '''生成端口定义的RTL'''
        return ['wire [%s:0] %s' % ((self.attribute.width-1),self.name_before_component)]


class IOSig(WireSig):

    @property
    def verilog_inst(self):
        '''生成端口实例化的RTL'''
        return [".%s(%s)" %(self.name_before_component,self.name_until_component)]

    @property
    def verilog_outer_def(self):
        '''生成信号声明的RTL'''
        return ["wire %s %s" %('' if self.attribute.width==1 else '[%s:0]' % (self.attribute.width-1),self.name_until_component)]

    @property
    def _iosig_type_prefix(self):
        raise NotImplementedError

    @property
    def verilog_def(self):
        return ['%s %s %s' % (self._iosig_type_prefix,'' if self.attribute.width==1 else '[%s:0]' %(self.attribute.width-1),self.name_before_component)]


class Input(IOSig):

    @property
    def is_lvalue(self):
        pass

    @property
    def lstring(self):
        return self.name_until_component #self.__name

    @property
    def rstring(self):
        return self.name_before_component #self.__name

    @property
    def _iosig_type_prefix(self):
        return 'input'

    def reverse(self):
        return Output(self.attribute)


class Output(IOSig):

    @property
    def is_lvalue(self):
        pass

    @property
    def lstring(self):
        return self.name_before_component #self.__name

    @property
    def rstring(self):
        return self.name_until_component #self.__name

    @property
    def _iosig_type_prefix(self):
        return 'output'

    def reverse(self):
        return Input(self.attribute)


class Inout(IOSig):

    @property
    def _iosig_type_prefix(self):
        return 'inout'

    def reverse(self):
        return Inout(self.attribute)


class Constant(WireSig):
    
    # def __init__(self,template=UInt(1,0)):
    #     self.__width = math.ceil(math.log(num,2))
    #     self.__value = num

    pass


class Bits(Constant):

    def __init__(self,width_or_string,value=0):
        super(Bits,self).__init__(self)
        if isinstance(width_or_string,int):
            self.__width = width_or_string
            self.__value = value
        elif isinstance(width_or_string,str):
            self.__width,self.__value = self._slove_wid_val_from_str(width_or_string)
        else:
            raise Exception('Input is not String or Int')

    def _slove_wid_val_from_str(self,string):
        mb = re.match('([0-9]+)(\'[bB])([01_]+)'        ,string)
        md = re.match('([0-9]+)(\'[dD])([0-9_]+)'       ,string)
        mh = re.match('([0-9]+)(\'[hH])([0-9a-fA-F_]+)' ,string)

        if mb:
            width = int(mb.group(1))
            value = int(mb.group(3).replace('_',''),2)
        elif md:
            width = int(md.group(1))
            value = int(md.group(3).replace('_',''),10)
        elif mh:
            width = int(mh.group(1))
            value = int(mh.group(3).replace('_',''),16)
        else:
            raise Exception()
        if value > (pow(2,width)-1):
            raise ArithmeticError('Overflow:%s' % string)
        return width,value


    @property
    def width(self):
        return self.__width

    @property
    def value(self):
        return self.__value

    @property
    def template(self):
        return self

    @property
    def string(self):
        return '%s\'b%s' % (self.__width,bin(self.__value).replace('0b','') )           #pass

    @property
    def rstring(self):
        return '%s\'b%s' % (self.__width,bin(self.__value).replace('0b','') )           #pass

    @property
    def lstring(self):
        raise NotImplementedError

    def __eq__(self,other):
        #print(self,other)
        #print(self.width,other.width)
        return True if type(self) == type(other) and self.width == other.width else False



class UInt(Bits):
    pass

class SInt(Bits):
    pass
  








class Parameter(SingleVar):

    @property
    def string(self):
        return self.name

    @property
    def rstring(self):
        return self.name

    @property
    def lstring(self):
        return self.name

    @property
    def verilog_assignment(self) -> str:
        if not hasattr(self,'_rvalue') or self._rvalue is None:
            return []
        else:
            return ['.%s(%s)' % (self.lstring,self._rvalue.rstring)]

    @property
    def verilog_def(self):
        return ['parameter %s = %s' % (self.lstring,self.attribute.rstring)]


    # @property
    # def width(self):
    #     return self.__width
# 
    # @property
    # def string(self):
    #     return self.name_before_component #self.__name
# 
    # @property
    # def attribute(self):
    #     return self.__width


    #@attribute.setter
    #def atrribute(self,value):
    #    self.__attribute = value




class GroupVar(Variable):

    def exclude(self,*str_list):
        pass


class IOGroup(GroupVar):

    def __init__(self):
        super(IOGroup,self).__init__()
        self._rvalue = None

    @property
    def io_list(self) -> list:
        return sorted([self.__dict__[k] for k in self.__dict__ if isinstance(self.__dict__[k],IOSig)])

    # += as circuit assignment
    def __iadd__(self,rvalue):
        if not isinstance(rvalue,IOGroup):
            raise ArithmeticError('A IOGroup expect assigned by a IOGroup.')
        # elif self.attribute != rvalue.attribute:
        #     raise ArithmeticError('Left value attribute/Right value attribute mismatch.')
        else:
            for iol,ior in zip(self.io_list,rvalue.io_list):
                #print(iol,ior)
                #print(iol,ior)
                #print(iol.width,ior.width)
                if isinstance(iol,Input):
                    ior += iol
                else:
                    iol += ior
            #print('%s get rvalue %s'  %(self,rvalue))
            object.__setattr__(self,'_rvalue',rvalue)
            #self.__rvalue = rvalue
        return self

    def exclude(self,*args):
        result = copy(self)
        for a in args:
            delattr(result,a)
        return result

    def __getitem__(self,*args):
        result = copy(self)
        for a in args:
            delattr(result,a)
        return result


    @property
    def verilog_assignment(self) -> str:
        return reduce(concat,[x.verilog_assignment for x in self.io_list],[])

  


    @property
    def verilog_def(self):
        return reduce(concat,[x.verilog_def for x in self.io_list],[])
    
    @property
    def verilog_outer_def(self):
        #print(self.name,self.io_list)
        #print(self.io_list[0].name,self.io_list[1].io_list)
        return reduce(concat,[x.verilog_outer_def for x in self.io_list],[])

    @property
    def verilog_inst(self):
        return reduce(concat,[x.verilog_inst for x in self.io_list],[])



    def reverse(self):
        reverse = IOGroup()
        for i in self.io_list:
            setattr(reverse,i.name,i.reverse())
        return reverse



    #def __setattr__(self,name,value):
    #    if not isinstance():
    #        pass




    # @property
    # def gen_rtl_io(self):
    #     '''生成信号声明的RTL'''
    #     return ["wire %s %s;" %('' if self.data_width==1 else '[%s:0]' % (self.data_width-1),self.name_until(Component))]

#from .Entity    import Entity
#from .Virtual import Virtual
#from .Component import Component
        #self.__name = None
        #if self.__name is None:
        #self.__get_name()

    #@property
    #def name(self):
    #    return self.__name

    #def __get_name(self):
    #    x = inspect.currentframe()
    #    while 1:
    #        for line in inspect.getframeinfo(x)[3]:
    #            m = re.search(r'([a-zA-Z0-9][a-zA-Z0-9_]*)\s*=\s*([a-zA-Z0-9][a-zA-Z0-9_]*)',line)
    #            if m:
    #                self.__name = m.group(1)
    #                return 
    #        x = x.f_back
