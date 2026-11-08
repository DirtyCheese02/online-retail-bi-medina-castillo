# C2 presentation dialogue

**Moisés Medina and Ignacia Castillo**  
**Language:** English  
**Rehearsal target:** approximately 12–13 minutes including chart pauses, with about 1,250 spoken words.  
**Slides:** 1–13 of the current presentation. Slide 14 is backup only.

Speak the named paragraphs. The slide titles and directions in italics are cues, not spoken text. The timing estimate assumes a measured pace with short pauses for the charts; rehearse once to establish your actual duration. Read “£” as “pounds” and decimal scores digit by digit, for example “zero point four six four.”

## 1. How do customers build recorded purchase value?

**Moisés:** Good morning. We are Moisés Medina and Ignacia Castillo. In C1, we studied customer concentration: who contributes most of the recorded purchase value? In C2, we ask how customers build that value. We use purchase frequency and average invoice value to explore different monthly purchase patterns.

## 2. C1 recap: customer concentration

**Ignacia:** In C1, the top ten percent of identified customers contributed sixty point five percent of identified purchase value. This suggested that a relatively small group deserved closer account review.

However, customer IDs covered only eighty-five point seven percent of eligible value. The remaining fourteen point three percent could not enter our customer ranking. Our conclusion was to review major accounts and investigate ID capture together.

That ranking gave us a starting point. It did not explain the purchase patterns behind each account's contribution.

## 3. The Online Retail case

**Moisés:** We use UCI Online Retail, a historical dataset from a UK gift retailer. Our analysis covers December 2010 to November 2011, using the same complete-month extract as W2.

The source contains about five hundred and sixteen thousand invoice lines. One line is one item entry on an invoice. Several lines form an invoice, and a customer may have several invoices.

For the model, we aggregate these into twelve thousand four hundred and eight active customer-month records. One record means one identified customer with eligible purchases in one month. The same customer can appear in several months.

We retain W2's purchase rules: positive quantity and price, non-cancellation invoices and the provisional merchandise-code rule. Missing-ID purchases remain visible in value coverage, but cannot enter customer profiles.

## 4. What we group, and why

**Moisés:** Why do we need more than total purchase value?

**Ignacia:** Imagine two customers who each record one thousand pounds in a month. One has a single invoice for one thousand pounds. The other has five invoices of two hundred pounds. Their total value is equal, but their purchase patterns differ.

**Moisés:** We represent this difference with two inputs. Frequency is the number of distinct eligible invoices in a customer-month. Average invoice value is that month's eligible value divided by its invoice count.

For example, two invoices totalling one hundred pounds give a frequency of two and an average invoice value of fifty pounds. We include all eligible identified customer-months, rather than restricting the model to C1's top ten percent.

## 5. Past months define the later evaluation

**Moisés:** We preserve the W2 time boundaries. December to July provides training, August and September provide validation, and October and November provide the test records.

Training contains seven thousand one hundred and ninety-five customer-months. Validation contains two thousand one hundred and ninety-two, and test contains three thousand and twenty-one.

Only training determines the transformation and model. The same customer can return later, but no invoice or customer-month crosses partitions. Earlier EDA already examined the full period, so this is a retrospective evaluation with prior exposure.

## 6. One model and one simple reference

**Moisés:** Our model is KMeans. It learns three centers and assigns records to the nearest center, grouping similar purchase patterns.

We chose three groups as a manageable first description. We have not established that three is the best possible number.

We first apply logarithms to reduce the influence of large ranges. Then we standardize the inputs, so invoice counts and pounds have comparable scales. We fit the scaler and centers using training data only, and keep them unchanged later.

**Ignacia:** Our simple reference groups records by total monthly value. Its lower and higher boundaries come from the training median and ninetieth percentile, approximately three hundred and thirty pounds and one thousand and thirty-seven pounds.

Both approaches use fixed rules on the same evaluation records. The reference tells us about contribution levels. KMeans explores frequency and invoice size together.

## 7. Validation checks before the test

**Moisés:** Before evaluating test records, we check that every validation record receives an assignment, all three profiles are populated, and the learned parameters remain unchanged.

We also calculate silhouette. It compares how close records are within their group with their distance to the nearest other group. Higher scores indicate clearer separation in these inputs.

KMeans obtains zero point four seven two, compared with zero point three zero zero for the value rule. We retain the prespecified first model, without searching for better test results. Silhouette is an internal separation measure; it does not measure prediction accuracy or commercial success.

## 8. The same records, two ways to group

*Pause briefly so the audience can locate the two charts.*

**Ignacia:** Each dot represents one of the same three thousand and twenty-one test customer-months. Further right means more invoices, and higher up means a larger average invoice value. Both charts use the same transformed coordinates and ranges.

The left chart colors records by the simple value rule. The right chart colors them by KMeans profile. The vertical bands appear because invoice counts are whole numbers.

These charts show the distinction behind our example: similar contribution levels can contain different combinations of frequency and invoice size.

## 9. Three profiles describe different purchase patterns

**Ignacia:** Profile one has smaller invoices. Its median invoice count is one, and its median average invoice value is about one hundred and fifty-two pounds.

Profile two generally has larger invoices, with a median count of one and a median average invoice value of about four hundred and sixteen pounds.

Profile three is more frequent, with a median count of two and a median average invoice value of about three hundred and thirteen pounds.

Profile three contains twenty-six point six percent of test records and contributes fifty-five percent of identified test value. These are monthly patterns and group medians. They do not establish permanent customer types, loyalty or profit.

## 10. A value tier can contain different purchase patterns

**Ignacia:** The higher-value reference tier contains three hundred and eighty test records. Of those, one hundred and twenty-four belong to profile two and two hundred and fifty-six belong to profile three.

This is the model's main addition: a higher-value tier contains different purchase patterns.

Test silhouette is zero point four six four for KMeans and zero point two eight nine for the value rule. KMeans shows clearer separation in the selected feature space. Because its objective also uses distances, that advantage does not establish better business decisions.

## 11. Earlier major accounts keep contributing

**Ignacia:** We also address the W2 feedback by following an earlier account group into later months. We fix the top three hundred and sixty-two identified accounts using purchases recorded through September.

Together, these accounts contribute about forty-eight percent of identified value in October and forty-six percent in November. Their contribution remains substantial, although their activity varies.

This is a separate account-contribution check. It does not validate the clusters. The monthly top ten percent has a different group size, and an account's absence in one month does not prove churn.

## 12. Missing IDs change the scope of the findings

**Ignacia:** In November, twenty-one point four five percent of eligible purchase value has no customer ID. That value remains outside both customer-grouping methods.

We show it as a separate value category. It may belong to many different people, so we cannot treat it as one customer or assign it one profile.

This is why the C1 conclusion still matters: account review and ID capture need attention together. Our profiles describe identified activity, rather than the retailer's entire customer population.

## 13. Model verdict and next step

**Moisés:** So, does the model work for our task? We retain this first model for descriptive profiling. It produces three interpretable groups in later records. Test silhouette is close to validation and higher than the simple reference on the same test records.

**Ignacia:** Commercial usefulness still needs validation. Our proposed next step is to examine recent transactions with verified customer linkage and review the profiles with business users. When contribution alone is the question, the simple value rule remains sufficient.

Our conclusion is that C1 identified concentration, and C2 adds a description of the purchase patterns behind contribution. We can use that description to structure account review, while keeping coverage and limitations visible. Thank you.

## 14. Reference comparison and sources — backup

*Do not present this slide during the main talk. Open it if asked about exact counts or sources.*

**Ignacia, if asked about the table:** These are the same three thousand and twenty-one test customer-months under both grouping methods. Rows are KMeans profiles and columns are the simple value tiers. The table shows how the groupings overlap. We have no true target labels, so it is not a confusion matrix.

---

## Essential answers to rehearse

**Why did C1 lead to this model?** C1 showed concentration by total purchase value. C2 asks whether that contribution comes from more frequent invoices, larger invoices, or different combinations of both.

**Does 0.464 mean 46.4% accuracy?** No. It is a silhouette score describing internal group separation in the selected transformed inputs. There are no known target labels for classification accuracy.

**Why not cluster only the top 10%?** We want to describe purchase patterns across eligible identified activity and retain the comparison with lower-value records. The C1 top decile motivates the account-review question, but does not define the clustering population.

**Is this ready for automatic marketing decisions?** Commercial usefulness and action effects remain unvalidated. The current model supports descriptive analyst review. Recent linked data and business-user review are the next steps.

**Preparation sources:** current C2 presentation; executed `01_C2_Customer_Profiles.ipynb`; C2 brief. Rounded spoken figures follow the displayed results. The reference cutoffs remain exact in code. This dialogue is a rehearsal aid and is not an additional Canvas deliverable.
