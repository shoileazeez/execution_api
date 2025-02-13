# import requests

# payload = {
#     "language": "python",
#     "version": "3.10",
#     "files": [
#         {
#             "name": "code.py",
#             "content": """nums = [int(x) for x in input().split()]
# target = int(input())

# def two_sum(nums, target):
#     num_map = {}
#     for i, num in enumerate(nums):
#         complement = target - num
#         if complement in num_map:
#             return [num_map[complement], i]
#         num_map[num] = i

# result = two_sum(nums, target)
# print(result)
# """
#         }
#     ],
#     "stdin": "2 7 11 15\n9"  # Corrected input placement
# }

# response = requests.post("https://emkc.org/api/v2/piston/execute", json=payload)
# print(response.json())


# import requests

# payload = {
#     "language": "python",
#     "version": "3.10",
#     "files": [
#         {
#             "name": "numpy_test.py",
#             "content": """import numpy as np

# # Generate large random matrices
# np.random.seed(42)
# matrix_a = np.random.randint(1, 100, (300, 300))
# matrix_b = np.random.randint(1, 100, (300, 300))

# # Matrix multiplication
# result = np.dot(matrix_a, matrix_b)

# # Print shape and first few values
# print("Result shape:", result.shape)
# print("First row:", result[0][:10])"""
#         }
#     ]
# }

# response = requests.post("https://emkc.org/api/v2/piston/execute", json=payload)
# print(response.json())

# import requests

# payload = {
#     "language": "python",
#     "version": "3.10",
#     "files": [
#         {
#             "name": "pandas_test.py",
#             "content": """import pandas as pd
# import numpy as np

# # Simulate a large dataset
# np.random.seed(42)
# data = {
#     'ID': range(1, 10001),
#     'Age': np.random.randint(18, 80, 10000),
#     'Salary': np.random.randint(30000, 150000, 10000),
#     'Department': np.random.choice(['HR', 'Tech', 'Finance', 'Marketing'], 10000)
# }

# df = pd.DataFrame(data)

# # Data cleaning
# df = df[df['Salary'] > 40000]  # Remove low salaries
# df['Age_Group'] = pd.cut(df['Age'], bins=[18, 30, 50, 80], labels=['Young', 'Mid', 'Senior'])

# # Aggregation
# summary = df.groupby('Department')['Salary'].mean()

# print("Processed DataFrame:\n", summary)
# """
#         }
#     ]
# }

# response = requests.post("https://emkc.org/api/v2/piston/execute", json=payload)
# print(response.json())

import requests

payload = {
    "language": "javascript",
    "version": "18.0.0",
    "files": [
        {
            "name": "js_test.js",
            "content": """console.time("Performance Test");

// Generate 1 million random numbers
let arr = Array.from({ length: 1_000_000 }, () => Math.floor(Math.random() * 1000000));

// Sort the array (O(n log n) complexity)
arr.sort((a, b) => a - b);

// Find the median
let median = arr.length % 2 === 0 ? (arr[arr.length / 2 - 1] + arr[arr.length / 2]) / 2 : arr[Math.floor(arr.length / 2)];

console.timeEnd("Performance Test");
console.log("Median Value:", median);
"""
        }
    ]
}

response = requests.post("https://emkc.org/api/v2/piston/execute", json=payload)
print(response.json())
