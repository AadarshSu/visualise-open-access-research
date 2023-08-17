import pandas as pd
from sqlalchemy import create_engine

# Create a database engine
engine = create_engine('sqlite:///mydatabase.db')

# Read the CSV file
df = pd.read_csv('institution-data-ror.csv')

# Save the data to a SQLite table
df.to_sql('institutions', engine, if_exists='replace', index=False)
