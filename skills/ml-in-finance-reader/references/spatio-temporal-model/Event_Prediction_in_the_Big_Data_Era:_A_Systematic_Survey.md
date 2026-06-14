# Event Prediction in the Big Data Era: A Systematic Survey: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/spatio-temporal-model/Event_Prediction_in_the_Big_Data_Era:_A_Systematic_Survey.pdf`  
Document type: survey/review  
Topic family: `spatio-temporal-model`  
Extracted text signal: 148,607 characters

## Distillation

This source addresses joint modeling of temporal dynamics and spatial, relational, or event structure.

Source-stated scope and claims:
- Event Prediction in the Big DataEra: A Systematic Survey LIANG ZHAO, EmoryUniversity Eventsareoccurrencesinspecificlocations,time,andsemanticsthatnontriviallyimpacteitheroursocietyor thenature,suchasearthquakes,civilunrest,systemfailures,pandemics,andcrimes.Itishighlydesirabletobe abletoanticipatetheoccurrenceofsucheventsinadvancetoreducethepotentialsocialupheavalanddamage caused.
- Due to the strong interdisciplinary nature of event prediction problems, most existing event prediction methods were initially designed to deal with specific application domains, though the techniques and evaluation procedures utilized are usually generalizableacrossdifferentdomains.However,itisimperativeyetdifficulttocross-referencethetechniquesacross different domains, given the absence of a comprehensive literature survey for event prediction.
- This article aimstoprovideasystematicandcomprehensivesurveyofthetechnologies,applications,andevaluationsof eventpredictioninthebigdataera.First,systematiccategorizationandsummaryofexistingtechniquesare presented,whichfacilitatedomainexperts’searchesforsuitabletechniquesandhelpmodeldevelopersconsolidatetheirresearchatthefrontiers.Then,comprehensivecategorizationandsummaryofmajorapplication domainsareprovidedtointroducewiderapplicationstomodeldeveloperstohelpthemexpandtheimpactsof theirresearch.Evaluationmetricsandproceduresaresummarizedandstandardizedtounifytheunderstandingofmodelperformanceamongstakeholders,modeldevelopers,anddomainexpertsinvariousapplication domains.Finally,openproblemsandfuturedirectionsarediscussed.Additionalresourcesrelatedtoeventpredictionareincludedinthepaperwebsite:http://cs.emory.edu/∼lzhao41/projects/event_prediction_site.html.
- Event Prediction in the Big Data Era: A Systematic Survey 94:3 thoseover65.However,byMay2018,72%oftheUnitedStatespopulationweresocialmediausers, including40%ofthoseover[29].Notonlythedatadistributionbutalsothenumberoffeaturesand input data sources can also vary in real time.

## Concepts And Methods

- `RNN`
- `LSTM`
- `GAN`
- `multimodal`
- `probabilistic forecasting`
- `attention`
- `point process`

## Finance Reading Lens

Translate space into a defensible point-in-time market relationship, then verify gains survive structural change and do not encode future outcomes.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Define relations point-in-time and document their update schedule.
- Use temporal tests with structural breaks and unseen entities.
- Compare temporal-only and relation-only ablations.
- Do not import physical invariance into adaptive markets without testing it.
- The PDF does not clearly center trading performance. Do not manufacture a Sharpe or tradability claim from its generic forecasting results.
- OOS or rolling-evaluation language was not clearly detected. Treat finance generalization as unproven until a chronological protocol is supplied.
- Finance or market language appears in the PDF. Check whether the finance evidence is a real evaluation domain, an illustrative example, or only motivation.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- 1 INTRODUCTION
- 1.1 Related Surveys
- 1.2 Outline
- 2 PROBLEM FORMULATION ANDPERFORMANCE EVALUATIONS
- 2.1 ProblemFormulation
- 2.2 EventPrediction Evaluation
- 2.2.1 MatchingPredictedEventsandRealEvents. Thefollowingtypesofmatchingaretypically
- evaluation.
- 2.2.2 Metrics of Effectiveness. The effectiveness of the event predictions is evaluated in terms
- 3 EVENTPREDICTION TECHNIQUES
- 3.1 Time Prediction
- 3.1.1 Occurrence Prediction. Occurrence prediction is arguably the most extensive, classical,

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
