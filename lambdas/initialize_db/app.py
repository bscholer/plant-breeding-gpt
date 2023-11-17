import boto3
from os import environ

# Assuming you are using RDS Data API to execute SQL statements
rds_data = boto3.client('rds-data')

def lambda_handler(event, context):
    # Define your SQL statements here
    sql_statements = [
        "CREATE TABLE IF NOT EXISTS plants (...);",
        # Add more SQL statements as needed
    ]
    
    # Execute each SQL statement
    for sql in sql_statements:
        response = rds_data.execute_statement(
            resourceArn=environ['AURORA_CLUSTER_ARN'],
            secretArn=environ['AURORA_SECRET_ARN'],
            database='plantsdb',  # The name of the database
            sql=sql
        )
        print(response)  # Log the response for each statement

    return {
        'statusCode': 200,
        'body': 'Database initialized successfully'
    }
