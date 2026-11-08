"""Package only the three artifact types permitted by the updated C2 brief."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json,shutil

HERE=Path(__file__).resolve().parent
delivery=HERE/'delivery';delivery.mkdir(exist_ok=True)
shutil.copyfile(HERE/'01_C2_Customer_Profiles.ipynb',delivery/'01_C2_Customer_Profiles.ipynb')
shutil.copyfile(HERE/'report/main.pdf',delivery/'GROUP_Medina_Castillo_C2_Brief.pdf')
names=['01_C2_Customer_Profiles.ipynb','GROUP_Medina_Castillo_C2_Brief.pdf','GROUP_Medina_Castillo_C2_Presentation.pptx']
path=delivery/'GROUP_Medina_Castillo_C2.zip'
with ZipFile(path,'w',ZIP_DEFLATED,compresslevel=9) as z:
    for name in names:
        assert (delivery/name).is_file(),name
        z.write(delivery/name,name)
with ZipFile(path) as z:
    assert sorted(z.namelist())==sorted(names)
    assert z.testzip() is None
manifest={name:hashlib.sha256((delivery/name).read_bytes()).hexdigest() for name in names}
manifest['GROUP_Medina_Castillo_C2.zip']=hashlib.sha256(path.read_bytes()).hexdigest()
(HERE/'outputs/submission_checksums.json').write_text(json.dumps(manifest,indent=2)+'\n',newline='\n')
print(path)
print('ZIP entries:',names)
print('ZIP bytes:',path.stat().st_size)
