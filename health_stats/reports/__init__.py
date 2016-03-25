
import graph.mean_glucose
import table.full_summary
import text.daily_summary

Reports = {
    # Graphs
    'graph:MeanGlucose': graph.mean_glucose.MeanGlucose,
    # Tables
    'table:FullSummary': table.full_summary.FullSummary,
    # Text logs
    'text:DailySummary': text.daily_summary.DailySummary,
}
