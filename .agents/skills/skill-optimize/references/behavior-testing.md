# Behavior testing

Apply this reference when you compare a revised skill with its previous version under pass 6. It sets how to build the cases, run the readers and judges, and report the result.

## Cases

- Write each case from the contract in pass 1. Give every changed rule at least one case whose expected outcome differs when the rule is misread or missing, and add cases for unchanged rules the edit could break.
- Write the expected outcomes and a scoring rubric before any reader runs. Mark each rubric item that tests a changed rule.
- Test routing only when the description changed. Identical descriptions give identical routing input, so a routing run then shows nothing.
- When the test environment cannot exercise a rule, such as one that needs a browser, a real tool call or a real wait, simulate the condition and state what the simulation cannot show, or list the rule as untested.
- When the number of runs is limited, spend runs first on cases for changed rules, then on repeats of those cases, then on other cases.

## Readers

- Give each reader a fresh context, one version of the skill and the case materials. Do not tell the reader which version it has or that a comparison exists.
- Assign versions to readers in a recorded order that balances the versions across cases.
- Collect the reader's final answer and every file it produced.

## Judges

- Give each judge the rubric and every file the reader received and produced. Withhold the version of each answer, and keep the mapping from answers to versions where the judges cannot read it.
- Require each verdict to quote, word for word, the answer or material it rests on. Check every quote against its source. Discard a verdict whose quotes do not occur in the source or that scores material its judge did not read. Disclose, without discarding the verdict, a defect in a judge's record that changes no evidence the verdict rests on, such as a misspelled file name in a read log.
- A judge that scores several answers in one context can compare them, which correlates its scores. Give each judge one answer when the run budget allows; otherwise disclose the correlation.
- When a verdict penalizes a defect of the test package rather than of the answer, such as a file the judge did not receive, report the raw score and the score with that item corrected, and name the defect.

## Reporting

- Report each version's score on the same rubric, and report the rubric items for changed rules separately.
- Describe a difference from one run per case and version as a trend, not an improvement. Describe equal results as no regression on those cases.
- List the cases removed, the rules left untested, each simulation and its limit, judge correlations, discarded verdicts and test-package defects.
