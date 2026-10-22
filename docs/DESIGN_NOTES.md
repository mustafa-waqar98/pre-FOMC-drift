# Design notes and open issues

Written before any post-2019 outcome was examined. Items marked VERIFY must be
checked against the primary source before they appear in the paper.

## Data issues that bind

**Daily data cannot test the hypothesis.** The claim is about the window that
ends before the statement. Close-to-close daily returns include the
announcement reaction, so they measure a different quantity. CRSP daily is
useful for infrastructure and for a full-day FOMC effect, but the headline
result needs intraday prices. Do not let the daily fallback stand in for the
real test.

**Statement release times varied in the early sample.** The calendar builder
applies 14:15 ET through February 2013 and 14:00 ET after, with a 15 minute
buffer. That is a rule, not a per-meeting observation. The flag
`release_time_verified` is 0 for every row. Lucca and Moench document actual
release times in their appendix; those should be merged in before the window is
cut. VERIFY.

**Press conference flag is incomplete.** Confirmed from the Fed's FEDS note of
2021-10-12: first press conference 2011-04-27, held at Summary of Economic
Projections meetings only through 2018, then after every meeting from
2019-01-30. The 2011 to 2018 SEP dates are not yet collected, so 62 meetings
carry a missing flag. This only affects the press conference subsample test,
not the main design. Fill from the Fed's SEP release history.

## Methodological concerns

**Episode clustering is the most serious threat.** The holdout has 53 meetings
and roughly half are classified anxious, but those anxious meetings cluster in
2020 and 2022. The effective number of independent volatility episodes is
closer to three or four than to 27. Heteroskedasticity-robust standard errors
will overstate precision. Inference should cluster at the episode level, or use
a randomization test that resamples episodes rather than days.

**The design is underpowered for the stated prior.** The proposal expects a
premium that is positive but smaller than the earlier estimate, while the
minimum detectable effect is about 90 bps against an earlier estimate of about
109 bps. The design can detect a full return of the premium and cannot
distinguish a half-sized premium from zero. That is the central weakness. The
honest framings are either to make the continuous VIX specification primary, or
to present the work as bounding the premium rather than testing a point
hypothesis. Options for recovering power, in rough order of cost: pool other
scheduled macro releases with an FOMC interaction; add other central banks for
independent variation; shorten the window to raise the signal to noise ratio.

**Decay timing is internally inconsistent in the draft.** The draft says decay
concentrates three to five years after publication and then counts from the
2011 working paper to get 2014 to 2016. Counting from the February 2015 journal
date gives 2018 to 2020 instead. Pick one clock and say which. Separately,
VERIFY that McLean and Pontiff actually make a three to five year claim; the
result I am confident of is the level decline in post-publication returns, not
a specific lag profile.

**Attribution of the 109 bps figure.** The draft credits Martello and Ribeiro
for roughly 109 bps in high implied volatility states. Hu, Pan, Wang and Zhu is
the paper that models the uncertainty premium. VERIFY which paper reports the
number and at what horizon before it anchors the power calculation, since the
whole hypothesis table is scaled to it.

**State definition can be contaminated by the meeting.** VIX going into a
meeting may already reflect meeting anticipation. The proposal's fix, measuring
the state a week earlier, is sound and should be the primary definition rather
than a robustness check.

**VIX comparability has changed.** Same-day option volume grew sharply after
2022, which affects what the index captures intraday. This matters for the
VIX-change test that separates communication from arbitrage, more than for the
return test.

## Holdout discipline

No estimate on data after 2019-12-31 has been run. The specification must be
frozen in `PRE_ANALYSIS_PLAN.md` and committed, with the code hash recorded,
before the holdout is touched. The test is run once.
