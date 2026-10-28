#!/usr/bin/env python3
"""Build every DevKit runtime file from editable source; no original binaries read.

Python 3.10+, GCC with -m32 code-generation support, GNU ld with i386pe.
The separate reference original/ directory is only read by --strict-original.
"""
from pathlib import Path
import argparse,hashlib,json,platform,shutil,subprocess,sys,zipfile,zlib
from dat_codec import encode as encode_dat
from gi_codec import encode as encode_gi
from scr_codec import build as build_scr

ROOT=Path(__file__).resolve().parent.parent
def sha(data):return hashlib.sha256(data).hexdigest()
def load(path):return json.loads(path.read_text('utf-8-sig'))
def run(*command):subprocess.run([str(v)for v in command],cwd=ROOT,check=True)
def version(command):return subprocess.check_output(command,text=True).splitlines()[0]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'dist')
    p.add_argument('--strict-original',action='store_true',help='require all rebuilt files to match the original SHA-256 manifest')
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'source';files={}
    for name,target in [('Main','CFG/Main.dat'),('CacheData','CFG/CacheData.dat'),('Lang','CFG/Rus/Lang.dat')]:
        files['DevKit/'+target]=encode_dat(load(source/'config'/(name+'.json')))
    files['DevKit/DATA/Script/Mod_DevKit.scr']=build_scr(source/'script/Mod_DevKit.rson',source/'script/Mod_DevKit.layout.json')
    for image in sorted((source/'graphics/layers').glob('*.json')):
        files['DevKit/DATA/FormShip2/'+image.stem+'.gi']=encode_gi(load(image))
    module=(source/'module/ModuleInfo.txt').read_text('utf-8-sig').replace('\r\n','\n').replace('\n','\r\n')
    files['DevKit/ModuleInfo.txt']=b'\xff\xfe'+module.encode('utf-16le')
    run(sys.executable,source/'native/wheel/build_wheel.py')
    files['DevKit/Native/DevKitWheel.dll']=(source/'native/wheel/DevKitWheel.dll').read_bytes()
    expected=load(ROOT/'original-file-sha256.json')
    if set(files)!=set(expected):raise SystemExit('Unexpected runtime file list')
    hashes={path:sha(data)for path,data in sorted(files.items())}
    differences=[path for path in hashes if hashes[path]!=expected[path]]
    if a.strict_original and differences:raise SystemExit('Original hash mismatch: '+repr(differences))
    stage=out/'mod';stage.mkdir(exist_ok=True)
    for path,data in files.items():
        dest=stage/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    package=out/'DevKit_v18_FROM_SOURCE.zip'
    with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as archive:
        for path,data in sorted(files.items()):
            info=zipfile.ZipInfo(path,date_time=(2026,10,28,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(package)as archive:
        if archive.testzip():raise SystemExit('ZIP CRC check failed')
    report={'schema':'devkit-source-build-v1','files':len(files),'source_derived_files':len(files),
            'original_runtime_binaries_used_as_build_inputs':False,
            'byte_identical_to_original':not differences,'different_files':differences,
            'python':platform.python_version(),'zlib':zlib.ZLIB_RUNTIME_VERSION,
            'gcc':version(['gcc','--version']),'ld':version(['ld','--version']),
            'sha256':hashes,'package_sha256':sha(package.read_bytes()),
            'rscript_executed':False,'game_executed':False}
    (out/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS:',len(files),'files rebuilt from source')
    print('Original hashes matched:',len(files)-len(differences),'/',len(files))
    print('Package:',package)

if __name__=='__main__':main()
