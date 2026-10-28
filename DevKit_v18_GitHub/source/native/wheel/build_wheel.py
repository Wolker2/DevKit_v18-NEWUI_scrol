from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent
BUILD=HERE/'build';BUILD.mkdir(exist_ok=True)
def run(*args):subprocess.run([str(a) for a in args],check=True)
flags=['-m32','-O2','-fno-pie','-fno-pic','-fno-asynchronous-unwind-tables','-fno-stack-protector','-fno-builtin']
apis={'kernel32':['GetCurrentThreadId'],
      'user32':['GetForegroundWindow','GetWindowThreadProcessId','ScreenToClient','SetWindowsHookExW','UnhookWindowsHookEx','CallNextHookEx','PostMessageW']}
libraries=[]
for lib,names in apis.items():
    (BUILD/(lib+'.c')).write_text('\n'.join('int '+n+'(void){return 0;}' for n in names)+'\n')
    (BUILD/(lib+'.def')).write_text('LIBRARY '+lib.upper()+'.dll\nEXPORTS\n'+''.join('    '+n+'\n' for n in names))
    run('gcc',*flags,'-c',BUILD/(lib+'.c'),'-o',BUILD/(lib+'.elf.o'))
    run(sys.executable,HERE/'elf_to_coff.py',BUILD/(lib+'.elf.o'),BUILD/(lib+'.obj'))
    library=BUILD/('lib'+lib+'.a');libraries.append(library)
    run('ld','-mi386pe','--dll','--entry','0','--no-insert-timestamp','--out-implib',library,'-o',BUILD/(lib+'_BUILD_ONLY.dll'),BUILD/(lib+'.obj'),BUILD/(lib+'.def'))
run('gcc','-O2','-Wall','-Wextra','-Werror',HERE/'test_wheel.c','-o',BUILD/'test_wheel')
run(BUILD/'test_wheel')
run('gcc',*flags,'-Wall','-Wextra','-Werror','-c',HERE/'devkit_wheel.c','-o',BUILD/'wheel.elf.o')
run(sys.executable,HERE/'elf_to_coff.py',BUILD/'wheel.elf.o',BUILD/'wheel.obj')
(BUILD/'wheel.def').write_text('LIBRARY DevKitWheel.dll\nEXPORTS\n    WheelEnable\n    WheelDisable\n')
run('ld','-mi386pe','--dll','--entry','_DllMain','--dynamicbase','--nxcompat','--enable-reloc-section','--no-insert-timestamp','-o',HERE/'DevKitWheel.dll',BUILD/'wheel.obj',*libraries,BUILD/'wheel.def')
print(HERE/'DevKitWheel.dll')
