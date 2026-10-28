"""Translate the two i386 relocation kinds emitted by this freestanding build.

No ABI translation: C uses explicit Win32 stdcall and 16-bit wide characters.
Reject any unrecognized relocation instead of producing a guessed binary.
"""
import struct
import sys
from pathlib import Path

def convert(source, destination):
    data=Path(source).read_bytes()
    assert data[:6]==b'\x7fELF\x01\x01'
    assert struct.unpack_from('<H',data,18)[0]==3
    offset=struct.unpack_from('<I',data,32)[0]
    width,count,names=struct.unpack_from('<HHH',data,46)
    assert width==40
    sections=[struct.unpack_from('<10I',data,offset+i*40) for i in range(count)]
    def blob(s):return data[s[4]:s[4]+s[5]]
    def string(buf,p):return buf[p:buf.index(0,p)].decode('ascii')
    section_strings=blob(sections[names])
    section_names=[string(section_strings,s[0]) for s in sections]
    allocated=[i for i,s in enumerate(sections) if s[2]&2 and s[1] in (1,8)]
    section_index={old:new+1 for new,old in enumerate(allocated)}
    sym_section=next(s for s in sections if s[1]==2)
    strings=blob(sections[sym_section[6]])
    symbols=[struct.unpack_from('<IIIBBH',data,sym_section[4]+p) for p in range(0,sym_section[5],16)]
    used=[]
    for i,(name,value,size,info,other,section) in enumerate(symbols):
        if not i or (info&15)==4:continue
        if section not in section_index and section not in (0,0xfff1):continue
        used.append(i)
    symbol_index={old:new for new,old in enumerate(used)}
    long_names=bytearray(b'\0\0\0\0')
    offsets={}
    def long_offset(name):
        if name not in offsets:
            offsets[name]=len(long_names);long_names.extend(name.encode('ascii')+b'\0')
        return offsets[name]
    def coff_name(name,section=False):
        encoded=name.encode('ascii')
        if len(encoded)<=8:return encoded.ljust(8,b'\0')
        position=long_offset(name)
        return (('/'+str(position)).encode('ascii').ljust(8,b'\0') if section else struct.pack('<II',0,position))
    payloads={i:bytearray(blob(sections[i])) if sections[i][1]!=8 else bytearray() for i in allocated}
    relocations={i:[] for i in allocated}
    for relocation in sections:
        if relocation[1]!=9 or relocation[7] not in section_index:continue
        target=relocation[7]
        for p in range(relocation[4],relocation[4]+relocation[5],8):
            address,info=struct.unpack_from('<II',data,p)
            symbol,kind=info>>8,info&255
            if kind not in (1,2):raise ValueError('Unsupported ELF relocation '+str(kind))
            if symbol not in symbol_index:raise ValueError('Relocation to omitted symbol')
            if kind==2:
                addend=struct.unpack_from('<I',payloads[target],address)[0]
                struct.pack_into('<I',payloads[target],address,(addend+4)&0xffffffff)
            relocations[target].append(struct.pack('<IIH',address,symbol_index[symbol],6 if kind==1 else 20))
    position=20+40*len(allocated)
    section_headers=[]
    chunks=[]
    for i in allocated:
        s=sections[i];raw=payloads[i];rel=b''.join(relocations[i]);raw_pointer=position if raw else 0
        chunks.append(raw);position+=len(raw)
        rel_pointer=position if rel else 0;chunks.append(rel);position+=len(rel)
        flags=0x40000000|0x00500000
        if s[2]&4:flags|=0x20000000|0x20
        elif s[1]==8:flags|=0x80
        else:flags|=0x40
        if s[2]&1:flags|=0x80000000
        section_headers.append(coff_name(section_names[i],True)+struct.pack('<6I2HI',0,0,s[5],raw_pointer,rel_pointer,0,len(relocations[i]),0,flags))
    coff_symbols=[]
    for old in used:
        name,value,size,info,other,section=symbols[old]
        text=section_names[section] if (info&15)==3 else '_'+string(strings,name)
        number=section_index.get(section,-1 if section==0xfff1 else 0)
        coff_symbols.append(coff_name(text)+struct.pack('<IhHBB',value,number,0x20 if (info&15)==2 else 0,2 if info>>4 else 3,0))
    struct.pack_into('<I',long_names,0,len(long_names))
    header=struct.pack('<HHIIIHH',0x14c,len(allocated),0,position,len(used),0,0x100)
    result=header+b''.join(section_headers)+b''.join(chunks)+b''.join(coff_symbols)+long_names
    Path(destination).write_bytes(result)

if __name__=='__main__':convert(sys.argv[1],sys.argv[2])
