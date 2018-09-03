import MMA8451

acc = MMA8451.MMA8451()
acc.begin()
for j in range(400):
    data = acc.read()
    if data is not None:
        print(data)
