import random

# 生成随机的汉字姓氏+数字
def generate_name():
    surnames = ['赵', '钱', '孙', '李', '周', '吴', '郑', '王']
    return random.choice(surnames) + str(random.randint(1, 99))

# 生成随机的18位数字，不能重复
def generate_ssn(used_ssns):
    ssn = ''.join(random.choices('0123456789', k=18))
    while ssn in used_ssns:
        ssn = ''.join(random.choices('0123456789', k=18))
    used_ssns.add(ssn)
    return ssn

# 生成随机的中国城市
def generate_address():
    cities = ['北京', '上海', '广州', '深圳', '杭州']
    return random.choice(cities)

# 生成浮点数工资
def generate_salary():
    return round(random.uniform(1000, 5000), 2)

# 生成随机的直接领导身份证号，一共是某个已经存在的ESSN
def generate_superssn(used_ssns, essn):
    # 防止循环引用
    potential_superssns = list(used_ssns - {essn})
    return random.choice(potential_superssns) if potential_superssns else None

# 生成随机的部门号
def generate_dno():
    return random.randint(1, 5)

# 生成EMPLOYEE关系的数据
def generate_employee_data(used_ssns):
    ename = generate_name()
    essn = generate_ssn(used_ssns)
    address = generate_address()
    salary = generate_salary()
    superssn = generate_superssn(used_ssns, essn)
    dno = generate_dno()
    return f'{ename},{essn},{address},{salary},{superssn},{dno}'

# 生成指定数量的数据并写入txt文件
def generate_and_write_data(file_path, num_records):
    used_ssns = set()
    with open(file_path, 'w') as file:
        for i in range(num_records):
            employee_data = generate_employee_data(used_ssns)
            file.write(employee_data + '\n')

# 调用函数生成并写入数据
generate_and_write_data('employee_data.txt', 50)
