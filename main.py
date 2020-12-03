
dict = {
    "c1":['c2','c3'],
    "c2":True,
    "c3":["c4"],
    "c4":True
}

holder = {
  "c1": 'rs',
  'c2': 'as_1',
  'c3': 'as_2',
  'c4': 'client'
}
test = dict['c1']

arr = []
for r in test:
  arr.append({'resource': r, 'issuer': holder[r]})

print(arr)