import requests

payload = {
    "language": "python",
    "version": "3.10",
    "files": [
        {
            "name": "code.py",
            "content": """nums = [int(x) for x in input().split()]
target = int(input())

def two_sum(nums, target):
    num_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i

result = two_sum(nums, target)
print(result)
"""
        }
    ],
    "stdin": "2 7 11 15\n9"  # Corrected input placement
}

response = requests.post("https://emkc.org/api/v2/piston/execute", json=payload)
print(response.json())

