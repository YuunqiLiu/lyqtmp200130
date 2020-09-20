# pylint: disable=unused-wildcard-import
from .pysrc.uhdl import *
# pylint: enable=unused-wildcard-import


def link(opl,opr):
    tmp =  opl
    tmp += opr

class sub1(Component):

    def __init__(self,DW=32):
        Component.__init__(self)
        self.DATA_WIDTH = Parameter(UInt(1))
        self.clk        = Input(UInt(1))
        self.rst        = Input(UInt(1))
        self.intr       = Output(UInt(1))
        #self.rst += self.DATA_WIDTH

class io0(IOGroup):

    def __init__(self):
        IOGroup.__init__(self)
        self.clk    = Input(UInt(1))
        self.rst    = Input(UInt(1))
        #print(self.__dict__)

class TestModule(Component):

    def __init__(self,DW=32):
        Component.__init__(self)
        self.clk    = Input(UInt(1))
        self.intr   = Output(UInt(1))
        self.op1    = Input(UInt(DW))
        self.op2    = Input(UInt(DW))
        self.op3    = Input(UInt(DW))
        self.res1   = Output(UInt(DW+1))
        self.res2   = Output(UInt(DW+1))
        self.cut    = Output(UInt(10))
        self.comb   = Output(UInt(DW*2))
        self.const  = Output(UInt(DW*2))
        self.input =  Input(UInt(1))
        self.output = Output(UInt(1))
        self.compare = Output(UInt(1))
        self.dff = Reg(UInt(DW),self.clk,self.intr)

        self.dff += self.op1
        #self.set_circuit('output',Output(UInt(1)))
        #self.set('output',Output(UInt(1)))

        self.output += self.input

        self.ingroup = io0()
        self.outgroup = io0().reverse()
        self.compare += Equal(self.op1,self.op2)

        self.sub1   = sub1()                      #实例化
        self.tmp    = Wire(UInt(DW))                    #定义Wire

        link(self.outgroup.exclude('rst'),self.ingroup.exclude('rst'))

        # tmp = self.outgroup.exclude('clk')
        # tmp += self.ingroup.exclude('clk')
        # self.outgroup['clk'] += self.ingroup['clk']

        self.sub1.clk += self.clk
        self.intr += self.sub1.intr


        self.tmp    += self.op1                   #赋值
        self.cut    += self.op1[9:0]              #截断
        self.comb   += Combine(self.op1,self.op2) #拼接
        self.const  += UInt(DW*2,64)              #常量
        self.res1   += self.tmp + self.op2        #二元运算
        self.res2   += self.op2 + self.op3

t = TestModule()
t.generate_verilog(iteration=True)

print(t.sub1.clk.name_before(t))
print(t.sub1.clk.name_until(t.sub1))

print(t.sub1.clk.ancestors())
print(t.sub1.clk.ancestors(until=t.sub1))
print(t.sub1.clk.ancestors(before=t))

#print(t.output.src_connect)
#print(t.input.des_connect)
# print(t.sub1.ancestors())
#t = test()

#self.cut  += CutExpression(self.op1,9,0)
#t.set_father_to_sub()
 # for l in t.output_list:
 #     print(l)
 #     print(l.name)
 #     print(l.verilog_assignment)
 #     print(l.verilog_def)
 #     print(l.verilog_inst)
 #     print(l.verilog_outer_def)

#print(t.output_list)
#print('23333')

#with open('result.v','w') as f:
#    #for i in t.verilog_def:
#    f.writelines([x+'\n' for x in t.verilog_def])

#print(t.verilog_def)
#print(t.verilog_inst)