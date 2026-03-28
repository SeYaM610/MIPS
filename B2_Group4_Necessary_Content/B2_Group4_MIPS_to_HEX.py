import re
import pprint as pp

OPC = {'A':'add','B':'addi','C':'sub','D':'subi','E':'and','F':'andi','G':'or','H':'ori','I':'sll','J':'srl','K':'nor','L':'lw','M':'sw','N':'beq','O':'bneq','P':'j'}
SEQ='GNCFLIMEPJDKHOBA'
INS={}
for i,v in enumerate(SEQ):
    INS[OPC[v]]=bin(i)[2:].zfill(4)

REG={'$zero':'0000','$t0':'0111','$t1':'0001','$t2':'0010','$t3':'0011','$t4':'0100','$sp':'0110'}
R=['add','sub','and','or','nor']
S=['sll','srl']
I=['addi','subi','andi','ori','beq','bneq','lw','sw']
J=['j']
ALU={'add':'000','sub':'001','and':'010','or':'011','nor':'100','sll':'101','srl':'110'}
DST0='1'
DST4='0'
SRCREG='0'
SRCINST='1'
MEMALU='0'
MEMMEM='1'

def ctrl(dst,src,mem,wr,rd,wrt,br,brn,jmp,alu):
    return hex(int(dst+src+mem+wr+rd+wrt+br+brn+jmp+alu,2))[2:].zfill(3)

lbl_cnt=0
def newlbl():
    global lbl_cnt
    c=lbl_cnt
    lbl_cnt+=1
    return 'L'+str(c)

def genctrl():
    print('Control ROM:')
    print('\t',end='')
    for c in SEQ:
        op=OPC[c]
        if op in R:
            print(ctrl(DST0,SRCREG,MEMALU,'1','0','0','0','0','0',ALU[op]),end=' ')
        elif op in S:
            print(ctrl(DST4,SRCINST,MEMALU,'1','0','0','0','0','0',ALU[op]),end=' ')
        elif op in I[:4]:
            print(ctrl(DST4,SRCINST,MEMALU,'1','0','0','0','0','0',ALU[op[:-1]]),end=' ')
        elif op in I[4:6]:
            b=('1','0') if op=='beq' else ('0','1')
            print(ctrl(DST4,SRCREG,MEMALU,'0','0','0',b[0],b[1],'0',ALU['sub']),end=' ')
        elif op in I[6:8]:
            if op=='sw':
                print(ctrl(DST4,SRCINST,MEMMEM,'0','0','1','0','0','0',ALU['add']),end=' ')
            else:
                print(ctrl(DST4,SRCINST,MEMMEM,'1','1','0','0','0','0',ALU['add']),end=' ')
        elif op in J:
            print(ctrl(DST4,SRCREG,MEMALU,'0','0','0','0','0','1',ALU['add']),end=' ')
    print()

ln_no=1
labels={}
def genlbl(lines):
    out=[]
    for l in lines:
        parts=[p.strip() for p in l.split(':')]
        if len(parts)==2:
            labels[parts[0]]=len(out)
            if parts[1]!='':
                out.append(parts[1])
        else:
            out.append(l)
    return out

def conv(ln,opc,*args):
    b=INS[opc]
    if opc in R:
        b+=REG[args[1]]+REG[args[2]]+REG[args[0]]
    elif opc in S:
        b+=REG[args[1]]+REG[args[0]]+bin(int(args[2]))[2:].zfill(4)
    elif opc in I:
        if opc in I[:6]:
            b+=REG[args[1]]
            imm=int(args[2]) if opc in I[:4] else labels[args[2]]-(ln+1)
        else:
            b+=REG[args[2]]
            imm=int(args[1])
        b+=REG[args[0]]
        if imm<0:
            imm=2**4+imm
        b+=bin(imm)[2:].zfill(4)
    elif opc in J:
        b+=bin(labels[args[0]])[2:].zfill(8)+'0000'
    return b

spat=r'[ \t,\(\)]+'
def splt(l): return re.split(spat,l)
STACK=True

if __name__=='__main__':
    pp.pprint(INS)
    genctrl()
    with open('input.asm') as f:
        lns=[x.split(r'//')[0].strip() for x in f]
        lns=list(filter(lambda x:x!='',lns))
    if STACK:
        re_sp=r'(push|pop)[ ]+(\$t[0-4])'
        orig=lns
        lns=['addi $sp, $zero, 15']
        for x in orig:
            m=re.search(re_sp,x)
            if not m:
                lns.append(x)
            else:
                if m.group(1)=='push':
                    lns.append(f'sw {m.group(2)}, 0($sp)')
                    lns.append('subi $sp, $sp, 1')
                else:
                    lns.append('addi $sp, $sp, 1')
                    lns.append(f'lw {m.group(2)}, 0($sp)')
    lns=genlbl(lns)
    pp.pprint(lns)
    binl=[]
    hexl=[]
    for i in range(len(lns)):
        bl=conv(i,*splt(lns[i]))
        binl.append(bl)
        hexl.append(hex(int(bl,2))[2:].zfill(4)+'\n')
    with open('output.bin','w') as bf:
        for i in range(len(lns)):
            bf.write(' '.join([binl[i][j:j+4] for j in range(0,len(binl[i]),4)])+' : '+lns[i]+'\n')
    with open('output.hex','w') as hf:
        hf.writelines(hexl)