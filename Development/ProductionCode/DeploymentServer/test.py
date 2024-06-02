# Dua input vao cho ham predict
predict_result = [3, 6]

# Chon subnet cho ket qua predict
subnet_targets = [0] * 4
for node in predict_result:
    if node in range(0, 1):
        subnet = 0
    elif node in range(2, 4):
        subnet = 1
    elif node in range(5, 7):
        subnet = 2
    elif node in range(8, 9):
        subnet = 3
    subnet_targets[subnet] = 1

print(subnet_targets)

# Write the subnet_targets to 'output.tmp' file
with open('output.tmp', 'w') as file:
    for target in subnet_targets:
        file.write(str(target) + '\n')