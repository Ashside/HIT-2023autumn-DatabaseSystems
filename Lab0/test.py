import random


def generate_hours():
    return round(random.uniform(0.5, 1), 2)


def generate_works_on_data(essn, project_numbers):
    num_projects = random.randint(1, len(project_numbers))  # 随机选择1到len(project_numbers)个项目
    selected_projects = random.sample(project_numbers, num_projects)

    works_on_data = []
    for pno in selected_projects:
        hours = generate_hours()
        works_on_data.append(f'{essn},{pno},{hours}')

    return works_on_data


def read_employee_data(file_path):
    employee_data = []
    with open(file_path, 'r') as file:
        for line in file:
            employee_data.append(line.strip().split(','))
    return employee_data


def generate_and_write_works_on(file_path, employee_data):
    project_numbers = [f'P{i}' for i in range(1, 11)]

    with open(file_path, 'w') as file:
        for _, essn, _, _, _, _ in employee_data:
            works_on_data = generate_works_on_data(essn, project_numbers)
            for data in works_on_data:
                file.write(data + '\n')


# 读取员工数据
employee_data = read_employee_data('employee_data.txt')

# 生成并写入WORKS_ON关系数据
generate_and_write_works_on('works_on_data.txt', employee_data)
