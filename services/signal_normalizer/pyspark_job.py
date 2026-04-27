from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, when

def run_normalization_job(input_path: str, output_path: str):
    spark = SparkSession.builder.appName("SignalNormalization").getOrCreate()
    
    # Read predictions
    predictions_df = spark.read.json(input_path)
    
    # Simple normalization logic
    signals_df = predictions_df.withColumn(
        "signal_type",
        when(col("model_type") == "churn", "RETAIN")
        .when(col("model_type") == "upsell", "UPSELL")
        .otherwise("IGNORE")
    ).withColumn(
        "urgency_level",
        when(col("score") > 0.8, "high")
        .when(col("score") > 0.5, "medium")
        .otherwise("low")
    )
    
    # Filter out strategic accounts if joined with CRM data
    # signals_df = signals_df.join(crm_accounts, "client_id", "left").filter(...)
    
    signals_df.write.mode("overwrite").parquet(output_path)
    
    spark.stop()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        run_normalization_job(sys.argv[1], sys.argv[2])
