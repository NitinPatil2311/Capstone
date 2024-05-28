from pymongo import MongoClient

# Function to fetch all historical data from the database
def fetch_all_tasks_from_db():
    connection = MongoClient('mongodb://localhost:27017/')
    db = connection['the_effort_estimation']
    task_data = db['tasks']
    data_from_collection = task_data.find({})
    all_tasks = [data for data in data_from_collection]
    connection.close()
    return all_tasks

# Calculation of estimated effort (hours)
def calculate_estimated_effort(task):
    complexity_input = {"low": 3, "medium": 4, "high": 5}
    size_input = {"small": 3, "medium": 4, "large": 5}
    complexity = complexity_input.get(task["complexity"], 0)
    size = size_input.get(task["size"], 0)
    # print("Complexity:", complexity)
    # print("Size:", size)
    eff = complexity * size
    return eff

# function to estimated efforts and confidence level
def cal_effort_and_confidence_level(complexity, size):
    tasks = fetch_all_tasks_from_db()
    complexity_input = {"low": 1, "medium": 2, "high": 3}
    size_input = {"small": 1, "medium": 2, "large": 3}
    complexity1 = complexity_input.get(complexity, 0)
    size1 = size_input.get(size,0)
    estimated_effort = []
    
    for task in tasks:
        effort = calculate_estimated_effort(task)
        estimated_effort.append(effort)
        # print(f"{task['title']}: Estimated Effort (hours) = {effort}")
        mean_effort = sum(estimated_effort) / len(estimated_effort)
    variance = sum((effort - mean_effort) ** 2 for effort in estimated_effort) / len(estimated_effort)
    
    z_value = 1.96  # Z-value for 95% confidence interval

    standard_deviation =  variance ** 0.5
    mean_effort = sum(estimated_effort) / len(estimated_effort)

    # Calculate margin of error
    margin_of_error = z_value * (standard_deviation / (len(estimated_effort) ** 0.5))

    # Calculate lower and upper bounds of the confidence interval
    lower_bound = mean_effort - margin_of_error
    upper_bound = mean_effort + margin_of_error

    total_effort = sum(estimated_effort)
    print(total_effort)
    mean_estimated_effort = total_effort / len(estimated_effort)
    print(mean_estimated_effort)
    # total_possible_effort = len(estimated_effort) * complexity1 * size1
    # conf_lev = (total_effort / total_possible_effort) * 100

    if mean_estimated_effort >= 16.55:
        confidence_level = "Low"
    elif 16.55 < mean_estimated_effort <= 16.70:
        confidence_level = "Medium"
    else:
        confidence_level = "High"

    # calculating estimated range (hours)
    min_estimated_range = lower_bound
    max_estimated_range = upper_bound
    print(confidence_level, mean_estimated_effort, min_estimated_range, max_estimated_range)
    return confidence_level, mean_estimated_effort, min_estimated_range, max_estimated_range
