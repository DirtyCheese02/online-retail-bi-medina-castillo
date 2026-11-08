"""Fresh-kernel execution with the current Python interpreter; path may be an extracted ZIP."""
import asyncio
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient

if sys.platform=='win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
path=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent/'01_C2_Customer_Profiles.ipynb'
nb=nbformat.read(path,4)
client=NotebookClient(nb,timeout=300,kernel_name='python3',resources={'metadata':{'path':str(path.parent)}})
client.km=client.create_kernel_manager()
client.km.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
client.execute();nbformat.write(nb,path)
print('Executed code cells:',sum(c.cell_type=='code' for c in nb.cells),'Saved:',path)
