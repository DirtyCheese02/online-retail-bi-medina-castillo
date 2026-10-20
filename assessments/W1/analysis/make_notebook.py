"""Create and execute the W1 notebook from the packaged CSV."""

from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient


HERE = Path(__file__).resolve().parent
OUT = HERE / "W1_online_retail.ipynb"

cells = [
    nbf.v4.new_markdown_cell("""# Workshop 1 | Online Retail, December 2010–November 2011

**Moisés Medina and Ignacia Castillo** · Business Intelligence IIB423T-1 · 25 September 2026

This is our first inspection of two possible C1 directions. The input is a date-filtered, otherwise uncleaned extract of the [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail). One row is a recorded invoice line, not an entire order or a customer. Values are in GBP. The CSV in `../data/` makes this notebook run after extracting the submission archive. AI assisted with drafting Python code; the team is responsible for the research choices and interpretation. See the report's Process record for limitations."""),
    nbf.v4.new_code_cell("""from pathlib import Path
import json
import pandas as pd
from IPython.display import display
from retail_analysis import load_case, write_outputs

ROOT = Path.cwd().resolve()
if ROOT.name == 'analysis':
    ROOT = ROOT.parent
DATA = ROOT / 'data'
FIGURES = ROOT / 'analysis' / 'figures'
df = load_case(DATA / 'online_retail_2010dec_2011nov_input.csv')
print('Rows, columns:', df.shape)
display(df.head(5))"""),
    nbf.v4.new_markdown_cell("""## 1. Scope and quality

We retain all eight UCI source columns and every row dated from 1 December 2010 through 30 November 2011. This gives 12 complete months. December 2011 ends on the ninth in the source, so it is not included in month comparisons. The checks below flag missing identifiers, missing descriptions, repeated identical rows, non-positive prices and special stock codes. We keep these rows in the input and apply explicit eligibility rules only when calculating each measure."""),
    nbf.v4.new_code_cell("""info, monthly_sales, monthly_cancel, products, countries, customers = write_outputs(df, DATA, FIGURES)
display(pd.DataFrame([info]).T.rename(columns={0: 'observed value'}))"""),
    nbf.v4.new_markdown_cell("""These quality checks can overlap; they are not a row-flow subtraction. We retain all rows in the input and apply exclusions only to a defined measure.

- **Customer ID:** A blank ID cannot be assigned to a person. We keep its purchase line in overall value and monthly context, but exclude it from customer ranking. Grouping all blank IDs as one customer would invent an account. Among eligible positive purchase lines, 121,721 have no ID; known IDs account for 85.7% of eligible value.
- **Description and duplicates:** A missing description does not remove quantity, price or stock code, so we keep it and use the code as a provisional product key. We also retain exact repeats because there is no line ID to distinguish an error from separate identical items; the report gives a deduplication sensitivity check.
- **Price:** The 2,463 non-positive-price rows comprise 2,461 recorded zeros and two negative-price bad-debt adjustments. A zero might reflect a gift, promotion, administrative entry or missing price, but there is no coupon field to verify why. We do not impute another order's price or a monthly product average because that would invent this transaction's charge. They remain in the input and are excluded from the priced-event measures.
- **Stock code and invoice flag:** The provisional five-digit merchandise pattern makes a comparable, reproducible scope for both candidates. Codes outside it include service/adjustment entries and product-like variants, so this boundary needs sensitivity testing. A `C` prefix is UCI's cancellation flag; it excludes a line from positive purchase value and is assessed under Candidate B's eligibility rules. A negative quantity without `C` is not automatically a confirmed customer cancellation.

Our business use is a retrospective customer portfolio review for A and a cancellation-process review for B. `Quantity × UnitPrice` on positive priced lines is observed line value, not profit or reconciled revenue; the dataset has no costs, payment reconciliation or promotion exposure."""),
    nbf.v4.new_markdown_cell("""## 2. Candidate A — customer concentration in purchase value

**Question:** How concentrated is *observed purchase-line value* among customers with an ID, and how does the contribution of customers observed in one invoice differ from that of others? A commercial analyst could use this to decide which customer groups deserve closer study. We include a row when its stock code follows the provisional five-digit merchandise pattern, its invoice does not start with `C`, and both quantity and unit price are positive. Line value is `Quantity × UnitPrice`. We then group by non-missing `CustomerID`. This is not profit, lifetime value, or a measure of all customers: missing IDs are excluded and the file covers only one year."""),
    nbf.v4.new_code_cell("""display(pd.DataFrame({
    'Measure': ['Customers with ID', 'Known-ID share of observed purchase value',
                'Top 1% customer share of known-ID value', 'Top 10% customer share of known-ID value',
                'Customers observed in one invoice', 'Their share of known-ID value'],
    'Value': [info['known_customers'], round(info['known_customer_id_value_share_pct'], 1),
              round(info['top_1pct_customer_value_share_pct'], 1),
              round(info['top_10pct_customer_value_share_pct'], 1),
              info['one_invoice_customers'], round(info['one_invoice_customer_value_share_pct'], 1)]
}))
display(__import__('IPython').display.Image(filename=str(FIGURES / 'customer_concentration.png')))
display(monthly_sales.round(2))
display(products.head(10).round(2))
display(countries.head(8).round(2))
display(__import__('IPython').display.Image(filename=str(FIGURES / 'monthly_purchase_value.png')))"""),
    nbf.v4.new_markdown_cell("""The top 10% of identifiable customers account for 60.5% of value within the known-ID subset; the top 1% account for 30.9%. Customers observed in only one invoice make up 36.1% of identifiable customers but 7.8% of their value. This supports examining concentration and repeat purchasing, but it does not establish loyalty or lifetime value. Customer IDs are missing on many lines, and the observation window may cut off earlier or later purchases. Monthly value is context: February 2011 is lowest and November highest, but a single annual cycle cannot establish a Christmas effect."""),
    nbf.v4.new_markdown_cell("""## 3. Candidate B — cancellation invoice patterns

**Question:** In which months and customer countries are cancellation invoice lines most visible? An operations analyst could prioritise a review of cancellation reasons and handling. We count merchandise rows with a `C` invoice, negative quantity and positive unit price. The monthly share uses **distinct eligible cancellation invoices divided by distinct eligible purchase plus cancellation invoices**. This is an event mix in the observed window, *not* the probability that a purchase was later cancelled: the source does not link a cancellation to its original invoice."""),
    nbf.v4.new_code_cell("""display(monthly_cancel.round(2))
display(countries.loc[countries.purchase_lines >= 1000, ['Country', 'purchase_lines', 'cancel_lines', 'cancel_line_share_pct']].round(2))
display(__import__('IPython').display.Image(filename=str(FIGURES / 'monthly_cancellation_share.png')))"""),
    nbf.v4.new_markdown_cell("""The cancellation invoice share is highest in January 2011 (about 18.6%) and lowest in November 2011 (about 12.6%). Germany and EIRE show higher cancellation-line shares than the United Kingdom among countries with at least 1,000 positive merchandise lines. Country is recorded as the customer's country, not necessarily the shipment destination. The period may omit the purchases associated with cancellations; no causal or product-quality claim follows from these shares."""),
    nbf.v4.new_markdown_cell("""## 4. Comparison and next decision

Candidate A has a direct value measure and a nontrivial customer-concentration question, but missing customer IDs and the finite observation window limit interpretation. Candidate B addresses a different operational question, but it cannot yet support a genuine purchase-level cancellation rate. We provisionally prefer A for C1 and ask the instructor whether B's descriptive cancellation mix is still a sufficiently useful second direction. Future ML could explore customer segments if ID coverage and timing are adequate; B would need a purchase–cancellation link and reason codes before predictive work. A dashboard could display contribution by customer group, observed invoice frequency and missing-ID coverage; B could show cancellation counts with denominators and data-quality flags."""),
]

nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
nbf.write(nb, OUT)
client = NotebookClient(nb, timeout=180, kernel_name="python3", resources={"metadata": {"path": str(HERE)}})
client.execute()
nbf.write(nb, OUT)
print(f"Executed and saved {OUT} with {len(nb.cells)} cells")
