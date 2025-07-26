
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv("locust_results_all.csv")

# Group by duration
grouped = df.groupby("duration")

# Benchmarks
ideal_response_time = 200
acceptable_response_time = 300

# Prepare results
results = []

for duration, group in grouped:
    response_times = group["response_time_ms"]
    success_count = group[group["success"] == True].shape[0]
    failure_count = group[group["success"] == False].shape[0]
    total_count = len(group)

    mean_response_time = response_times.mean()

    success_rate = round(success_count / total_count * 100, 2)
    failure_rate = round(failure_count / total_count * 100, 2)

    results.append({
        "Test Duration": duration,
        "Requests": total_count,
        "Min RT (ms)": round(response_times.min(), 2),
        "Max RT (ms)": round(response_times.max(), 2),
        "Mean RT (ms)": round(mean_response_time, 2),
        "Std Dev RT (ms)": round(response_times.std(), 2),
        "Success Rate (%)": success_rate,
        "Failure Rate (%)": failure_rate,
        "Δ from 200ms (Ideal)": round(mean_response_time - ideal_response_time, 2),
        "Δ from 300ms (Acceptable)": round(mean_response_time - acceptable_response_time, 2),
        "FHIR Compliance (%)": success_rate,
        "FHIR Non-Compliance (%)": failure_rate
    })

# Convert to DataFrame
summary_df = pd.DataFrame(results)
summary_df["Test Duration"] = pd.Categorical(summary_df["Test Duration"], categories=["1m", "5m", "10m"], ordered=True)
summary_df = summary_df.sort_values("Test Duration")

# Print summary table
print("\n=== Locust Test Summary by Duration ===\n")
print(summary_df.to_string(index=False))

# Save to Excel
summary_df.to_excel("locust_summary.xlsx", index=False)
print("\nSaved summary table to 'locust_summary.xlsx'.")

# Mean Response vs Benchmarks Graph (no title)
plt.figure(figsize=(10, 6))
durations = summary_df["Test Duration"]
mean_rts = summary_df["Mean RT (ms)"]

plt.bar(durations, mean_rts, color="#4c72b0", label="Mean RT")
plt.axhline(ideal_response_time, color="green", linestyle="--", linewidth=2, label="Ideal (200ms)")
plt.axhline(acceptable_response_time, color="orange", linestyle="--", linewidth=2, label="Acceptable (300ms)")

plt.xlabel("Test Duration")
plt.ylabel("Mean Response Time (ms)")
plt.legend()
plt.tight_layout()
plt.savefig("response_time_comparison.png")
plt.show()

# Mean Response Time with Std Dev Error Bars (no title)
plt.figure(figsize=(10, 6))
plt.bar(
    summary_df["Test Duration"],
    summary_df["Mean RT (ms)"],
    yerr=summary_df["Std Dev RT (ms)"],
    capsize=10,
    color="#4c72b0",
    edgecolor="black"
)
plt.xlabel("Test Duration")
plt.ylabel("Mean Response Time (ms)")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig("mean_rt_with_stddev.png")
plt.show()

#FHIR Compliance Bar Chart
plt.figure(figsize=(10, 6))
plt.bar(
    summary_df["Test Duration"],
    summary_df["FHIR Compliance (%)"],
    color="#4c72b0",
    edgecolor="black",
    label="FHIR Compliant"
)
plt.bar(
    summary_df["Test Duration"],
    summary_df["FHIR Non-Compliance (%)"],
    bottom=summary_df["FHIR Compliance (%)"],
    color="#d62728",
    edgecolor="black",
    label="Non-Compliant"
)
plt.xlabel("Test Duration")
plt.ylabel("FHIR Validation Result (%)")
plt.legend()
plt.tight_layout()
plt.savefig("fhir_compliance_chart.png")
plt.show()

