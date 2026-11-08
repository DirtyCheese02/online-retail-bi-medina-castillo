"""Reviewer-facing response to W2 feedback, recorded from the team on 2026-11-08."""
from pathlib import Path
import ast
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/DirtyCheese02/online-retail-bi-medina-castillo'
RELEASE = 'w2-feedback-2026-11-08'
BASELINE_SHA = 'd33a27c97a3bb9e6b31fb9cb23be83156c11d0f3'


def link(path: str) -> str:
    return f'{REPO}/blob/{RELEASE}/{path}'


def response_table() -> pd.DataFrame:
    rows = [
        ('C2', 3, 'Seventeen checks were reported, but their executable notebook was not received.',
         'Provide the executed English notebook and the validate implementation with saved quality outputs.',
         'notebooks/W2_project.ipynb; src/w2_analysis.py; data/processed/quality_checks.csv',
         'Fresh-kernel run; 17 quality-check results and source-row conservation.'),
        ('D2', 2, 'The invoice-stratified sample had no received code or selected identifiers.',
         'Expose the fixed-seed sampling function, selected invoice IDs, monthly strata and actual sample.',
         'src/w2_analysis.py; data/processed/sample_invoice_ids.csv; data/processed/sample_strata.csv; data/processed/invoice_sample_25pct.csv.gz',
         'Verify seed 4232026, monthly invoice counts and all lines per selected invoice.'),
        ('F2', 4, 'Split counts and zero invoice overlap could not be checked against delivered subsets/code.',
         'Link the three actual subsets, row memberships, nested construction and overlap implementation.',
         'data/splits/train.csv.gz; data/splits/validation.csv.gz; data/splits/test.csv.gz; data/processed/split_membership.csv; data/processed/split_overlap.csv',
         'Check actual subset union, date limits, unique source rows and zero shared invoices.'),
        ('F3', 2, 'Train-only StandardScaler fitting was described without accessible implementation.',
         'Expose the preprocessing function, fitted parameters and transformed invoice-level values.',
         'src/w2_analysis.py; evidence/preprocessing_parameters.json; data/processed/invoice_preprocessing.csv',
         'Recalculate the mean/scale from 11,040 training invoices and verify the unchanged transform.'),
        ('F4', 2, 'The validation gate and exclusion of test were not inspectable.',
         'Expose the ordered fit/validation/test code and execution log, with failure before test transformation.',
         'src/w2_analysis.py; data/processed/validation_execution.csv; data/processed/split_hierarchy.csv',
         'Assert validation belongs to development, train-only fit and gate completion before test transform.'),
        ('G1', 2, 'The received files had only the supplemental PDF, without notebook, README or direct GitHub link.',
         'Provide the executed notebook and README as primary hand-in files, plus direct versioned links in the PDF.',
         'notebooks/W2_project.ipynb; README.md; SUBMISSION.md',
         'Check local hand-in files and public versioned URLs; the PDF alone is not the complete hand-in.'),
        ('G2', 1, 'The PDF omitted a repository URL and verifiable W2 SHA/tag.',
         'Add repository URL, corrective release tag, immutable analysis-baseline SHA and direct evidence links.',
         'report/GROUP_Medina_Castillo_W2_Report.pdf; evidence/submission_identity.json; SUBMISSION.md',
         'Inspect PDF link annotations and resolve the public release tag after publication.'),
    ]
    table = pd.DataFrame(rows, columns=['criterion', 'points_deducted', 'received_feedback',
                                      'corrective_action', 'evidence_paths', 'verification'])
    table['status'] = 'Evidence made accessible in corrective release; no regrade claimed'
    for paths in table.evidence_paths:
        for path in paths.split('; '):
            assert (ROOT / path).is_file(), path
    table.to_csv(ROOT / 'evidence/W2_feedback_response.csv', index=False)
    return table


def code_link(function: str) -> str:
    tree = ast.parse((ROOT / 'src/w2_analysis.py').read_text(encoding='utf-8'))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
    return link('src/w2_analysis.py') + f'#L{node.lineno}'


def value_scope_bridge() -> pd.DataFrame:
    """Keep unidentified value as an aggregate bucket, never as a fabricated customer."""
    baseline = json.loads((ROOT / 'data/processed/w2_metrics.json').read_text())['baseline']
    coverage = baseline['ID_coverage_pct'] / 100
    top_share = baseline['K10_pct'] / 100
    table = pd.DataFrame({
        'value_bucket': ['Known-ID top 10% group', 'Other known-ID purchases', 'Unidentified purchases'],
        'share_of_all_eligible_value_pct': [100 * coverage * top_share,
                                          100 * coverage * (1 - top_share), 100 * (1 - coverage)],
    })
    assert abs(table.share_of_all_eligible_value_pct.sum() - 100) < 1e-10
    table.to_csv(ROOT / 'evidence/value_scope_bridge.csv', index=False)
    return table


def write_identity() -> dict:
    identity = {'feedback_recorded_on': '2026-11-08', 'repository_url': REPO,
                'corrective_release_tag': RELEASE,
                'analysis_baseline_sha': BASELINE_SHA,
                'baseline_role': 'Immutable pre-feedback executable analysis; analytical rules/results unchanged',
                'corrective_release_tree_url': f'{REPO}/tree/{RELEASE}',
                'primary_notebook_url': link('notebooks/W2_project.ipynb'),
                'readme_url': link('README.md')}
    (ROOT / 'evidence/submission_identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    return identity


if __name__ == '__main__':
    write_identity()
    print(value_scope_bridge().to_string(index=False))
    print(response_table()[['criterion', 'corrective_action']].to_string(index=False))
