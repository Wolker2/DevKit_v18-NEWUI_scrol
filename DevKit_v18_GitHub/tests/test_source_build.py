import copy,hashlib,json,shutil,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from scr_codec import encode
from inspect_scr import parse
from gi_codec import encode as encode_gi,decode as decode_gi

def load(p):return json.loads(p.read_text('utf-8-sig'))

class SourceBuildTests(unittest.TestCase):
    def setUp(self):
        self.scene=load(ROOT/'source/script/Mod_DevKit.rson')
        self.layout=load(ROOT/'source/script/Mod_DevKit.layout.json')

    def parse_bytes(self,data):
        with tempfile.TemporaryDirectory()as folder:
            path=Path(folder)/'script.scr';path.write_bytes(data);return parse(path)

    def test_entire_scr_independent_structural_roundtrip(self):
        original=ROOT/'original/DevKit/DATA/Script/Mod_DevKit.scr'
        built=encode(self.scene,self.layout)
        self.assertEqual(built,original.read_bytes())
        decoded=self.parse_bytes(built)
        self.assertEqual(decoded,parse(original))
        self.assertEqual(len(decoded['global_variables']),1)
        self.assertEqual(len(decoded['local_variables']),34)
        self.assertEqual([len(decoded[k])for k in ('dialogs','messages','answers')],[4,14,78])

    def test_editable_code_rebuilds_and_relocates_header(self):
        for group in self.scene['Visual.Objects']:
            for item in group.get('Operations',[]):
                if item.get('Name')=='global_code':
                    item['Code'].insert(0,'// source modification test\r')
        data=encode(self.scene,self.layout);decoded=self.parse_bytes(data)
        self.assertTrue(decoded['global_code'].startswith('// source modification test\r\n'))
        self.assertGreater(decoded['local_offset'],73)
        self.assertEqual(len(decoded['answers']),78)

    def test_editable_variable_initialization_is_used(self):
        for group in self.scene['Visual.Objects']:
            for item in group.get('Variables',[]):
                if item['Name']=='DevKitVisibility':item['Init']='2'
        self.assertEqual(self.parse_bytes(encode(self.scene,self.layout))['global_variables'][0]['value'],2)

    def test_all_graphics_roundtrip_and_pixel_edit(self):
        for path in sorted((ROOT/'source/graphics/layers').glob('*.json')):
            source=load(path);binary=encode_gi(source)
            original=ROOT/'original/DevKit/DATA/FormShip2'/(path.stem+'.gi')
            self.assertEqual(binary,original.read_bytes(),path.name)
            self.assertEqual(decode_gi(binary),source,path.name)
        source=load(ROOT/'source/graphics/layers/DevKitPanelBG.json')
        packet=next(c for c in source['layers'][0]['commands']if 'pixels'in c)
        packet['pixels'][0]^=1
        self.assertEqual(decode_gi(encode_gi(source)),source)

    def test_build_without_any_original_or_prebuilt_binary(self):
        with tempfile.TemporaryDirectory()as folder:
            target=Path(folder)
            shutil.copytree(ROOT/'source',target/'source',ignore=shutil.ignore_patterns('build','*.dll','__pycache__'))
            shutil.copytree(ROOT/'scripts',target/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copy2(ROOT/'original-file-sha256.json',target/'original-file-sha256.json')
            result=subprocess.run([sys.executable,str(target/'scripts/build.py'),'--strict-original'],cwd=target,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+'\n'+result.stderr)
            report=load(target/'dist/build-report.json')
            self.assertTrue(report['byte_identical_to_original'])
            self.assertFalse(report['original_runtime_binaries_used_as_build_inputs'])
            with zipfile.ZipFile(target/'dist/DevKit_v18_FROM_SOURCE.zip')as archive:
                self.assertIsNone(archive.testzip())
                expected=load(ROOT/'original-file-sha256.json')
                self.assertEqual(len(archive.namelist()),22)
                for name,digest in expected.items():self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(),digest)

if __name__=='__main__':unittest.main()
