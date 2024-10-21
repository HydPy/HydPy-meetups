import pandas as pd
from memory_profiler import profile

@profile
def process_data():
    df = pd.DataFrame({'a': range(1000000), 'b': range(1000000)})
    df['c'] = df['a'] + df['b']
    df = df.drop(columns=['a'])
    return df

# Step 3: Use %mprun to profile the function
process_data()
