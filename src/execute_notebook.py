"""Execute the submitted notebook from a fresh kernel and save outputs in place."""
import asyncio
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient

if sys.platform=='win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
root=Path(__file__).resolve().parents[1]
path=root/'notebooks/W2_project.ipynb'
notebook=nbformat.read(path,as_version=4)
client=NotebookClient(notebook,timeout=300,kernel_name='python3',
                      resources={'metadata':{'path':str(root)}})
client.km=client.create_kernel_manager()
client.km.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
client.execute()
nbformat.write(notebook,path)
print(f'Executed {sum(c.cell_type=="code" for c in notebook.cells)} code cells; saved all outputs.')
