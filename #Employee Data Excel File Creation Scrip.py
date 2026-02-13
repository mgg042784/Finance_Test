#Employee Data Excel File Creation Script
import pandas as pd

# Create sample employee data
data = {
    'ID': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
    'First Name': ['John', 'Sarah', 'Michael', 'Emily', 'David', 'Jessica', 'Robert', 'Jennifer', 'James', 'Linda'],
    'Last Name': ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'],
    'Salary': [65000, 75000, 85000, 70000, 80000, 78000, 92000, 68000, 88000, 72000],
    'Tenure': [3, 7, 5, 2, 8, 4, 10, 1, 6, 5]
}

# Create DataFrame
df = pd.DataFrame(data)

# Write to Excel
output_file = r'c:\Users\mgrac\OneDrive\Documents\Employee_Data.xlsx'
df.to_excel(output_file, index=False, sheet_name='Employees')
print(f'Excel file created: {output_file}')