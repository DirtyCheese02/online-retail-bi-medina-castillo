"""Stage the three required attachment files plus the exact release identity; no upload."""
import hashlib
import json
from pathlib import Path
import subprocess

from feedback_delivery import ROOT, REPO, RELEASE


def main():
    sha = subprocess.check_output(['git', 'rev-parse', RELEASE + '^{commit}'], cwd=ROOT, text=True).strip()
    target = ROOT.parent / 'WorkShops/GROUP_Medina_Castillo_W2_Corrected'
    target.mkdir(parents=True, exist_ok=True)
    paths = ['notebooks/W2_project.ipynb', 'README.md', 'report/GROUP_Medina_Castillo_W2_Report.pdf']
    manifest = []
    for rel in paths:
        source = ROOT / rel
        destination = target / source.name
        expected = subprocess.check_output(['git', 'show', sha + ':' + rel], cwd=ROOT)
        # Copy the exact release blob; avoid accidental working-tree changes in the hand-in.
        destination.write_bytes(expected)
        assert destination.read_bytes() == expected
        manifest.append({'attachment': destination.name, 'repository_path': rel,
                         'sha256': hashlib.sha256(expected).hexdigest()})
    text = (f'W2 corrective hand-in\nTeam: Moises Medina and Ignacia Castillo\n'
            f'Repository: {REPO}\nSubmitted commit SHA: {sha}\n'
            f'Release tag: {RELEASE}\nVersioned tree: {REPO}/tree/{sha}\n\n'
            'Attach W2_project.ipynb and README.md; include the PDF as a supplement. '
            'Paste the repository, full SHA and tree link above into the submission form.\n'
            'For execution, clone this full repository version: source modules and data '
            'are included there. These three attachment copies are not a standalone project.\n'
            'No files have been uploaded to Canvas by this staging operation.\n')
    (target / 'HAND_IN.txt').write_text(text, encoding='utf-8')
    (target / 'ATTACHMENT_CHECKSUMS.json').write_text(json.dumps(
        {'release_commit': sha, 'attachments': manifest, 'upload_receipt': 'Not verified; user must upload'},
        indent=2) + '\n')
    print(target)
    print('Verified attachment copies:', len(manifest))


if __name__ == '__main__':
    main()
