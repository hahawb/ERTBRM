import matplotlib
matplotlib.use('Agg')  # 设置Agg后端，应该在导入pyplot之前设置
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime

# 创建保存图像的目录
save_dir = r'C:\Users\X1\Desktop\result'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def initialize_nodes(num_nodes=100, behavior_probs=[0.6, 0.2, 0.2], seed=None):
    if seed is not None:
        np.random.seed(seed)
    behaviors = ['stable', 'declining', 'random']
    nodes = []
    for _ in range(num_nodes):
        behavior = np.random.choice(behaviors, p=behavior_probs)
        if behavior == 'stable':
            vote = lambda task, step: True
            accuracy = np.random.uniform(0.5, 0.8)
        elif behavior == 'declining':
            vote = lambda task, step: False
            accuracy = np.random.uniform(0.2, 0.4)
        else:
            vote = lambda task, step: np.random.choice([True, False])
            accuracy = np.random.uniform(0.3, 0.7)

        nodes.append({
            'behavior': behavior,
            'load': np.random.uniform(10,15),
            'time': 0,
            'positive_streak': 0,
            'negative_streak': 0,
            'accuracy': accuracy,
            'vote': vote,
            'consecutive_selections': 0,
            'speed': 10
        })
    return nodes

def generate_task(seed=None):
    if seed is not None:
        np.random.seed(seed)
    return {'duration': np.random.choice([5, 10, 15])}

def update_consecutive_selections(nodes, selected_indices):
    for idx, node in enumerate(nodes):
        if idx in selected_indices:
            node['consecutive_selections'] += 1
        else:
            node['consecutive_selections'] -= 1

def update_speed(nodes, task, selected_indices):
    for idx, node in enumerate(nodes):
        if idx in selected_indices:
            # 调整速度计算方式，确保速度不会过低
            node['speed'] = max(5, node['speed'] - 0.1 * task['duration'])
        else:
            node['speed'] = min(15, node['speed'] + 0.1)  # 未被选中的节点速度逐渐恢复

def select_nodes(nodes, dynamic):
    if dynamic:
        selections = sorted(( node['load']/ node['speed'], idx) for idx, node in enumerate(nodes))
        selected_indices_15 = [idx for _, idx in selections[:30]]
        accuracy_scores = [(nodes[idx]['accuracy'], idx) for idx in selected_indices_15]
        accuracy_scores.sort(reverse=True)
        selected_indices = [idx for _, idx in accuracy_scores[:7]]
    else:
        selected_indices = np.random.choice(len(nodes), 7, replace=False).tolist()
    return selected_indices

def update_accuracy(nodes, selection_indices, votes, task):
    # Correctly count true votes from the list of boolean votes
    majority_vote = sum(votes) > len(votes) / 2
    for idx in selection_indices:
        node = nodes[idx]
        node_vote = node['vote'](task, len(node.get('history', [])))  # task is now available
        if (node_vote == majority_vote):
            node['positive_streak'] += 1
            node['negative_streak'] = 0
            increase = (1 - node['accuracy']) * 0.05 * node['positive_streak']
            node['accuracy'] = min(node['accuracy'] + increase, 1)
        else:
            node['negative_streak'] += 1
            node['positive_streak'] = 0
            decrease = node['accuracy'] * 0.1 * node['negative_streak']
            node['accuracy'] = max(node['accuracy'] - decrease, 0)


def execute_cumulative_tasks(nodes, task, dynamic=True):
    selection_indices = select_nodes(nodes, dynamic)
    votes = [nodes[idx]['vote'](task, len(nodes[idx].get('history', []))) for idx in selection_indices]
    for idx in selection_indices:
        nodes[idx]['time'] +=  task['duration']/ nodes[idx]['speed']
        nodes[idx]['load'] +=  nodes[idx]['time']
    update_accuracy(nodes, selection_indices, votes, task)
    update_consecutive_selections(nodes, selection_indices)
    update_speed(nodes, task, selection_indices)
  

    true_votes = sum(votes)
    false_votes = len(votes) - true_votes
    correct_decision = true_votes > false_votes
    
    total_task_time = max(nodes[idx]['time'] for idx in selection_indices)
    return correct_decision, total_task_time

# Main simulation code
nodes_dynamic = initialize_nodes()
nodes_random = initialize_nodes()
average_load = 0  # 初始化平均负载
tasks = []

total_correct_dynamic = 0
total_correct_random = 0
total_time_dynamic = 0
total_time_random = 0
accuracies_dynamic = []
accuracies_random = []
times_dynamic = []
times_random = []

num_tasks = 100
for i in range(num_tasks):
    task_dynamic = generate_task()
    task_random = generate_task()
    tasks.append(task_dynamic)
    correct_dynamic, time_dynamic = execute_cumulative_tasks(nodes_dynamic, task_dynamic, dynamic=True)
    correct_random, time_random = execute_cumulative_tasks(nodes_random, task_random, dynamic=False)
    total_correct_dynamic += correct_dynamic
    total_correct_random += correct_random
    total_time_dynamic += time_dynamic
    total_time_random += time_random
    if (i + 1) % 10 == 0 or i == num_tasks - 1:
        accuracies_dynamic.append((total_correct_dynamic / (i + 1)) * 100)
        accuracies_random.append((total_correct_random / (i + 1)) * 100)
        times_dynamic.append(total_time_dynamic)
        times_random.append(total_time_random)

x_ticks = range(10, num_tasks + 1, 10)

average_time_savings_percentage = np.mean([(r - d) / d * 100 if d != 0 else 0 for d, r in zip(times_dynamic, times_random)])
average_accuracy_improvement_percentage = np.mean([(d - r) / r * 100 if r != 0 else 0 for d, r in zip(accuracies_dynamic, accuracies_random)])

print("Average Time Savings: {:.1f}%".format(average_time_savings_percentage))
print("Average Accuracy Improvement: {:.1f}%".format(average_accuracy_improvement_percentage))

def save_plot_with_timestamp(directory, base_filename, figure):
    if not os.path.exists(directory):
        os.makedirs(directory)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}.png"
    figure.savefig(os.path.join(directory, filename))
    plt.close(figure)

# 任务完成时间图
plt.figure(figsize=(10, 6))
plt.plot(list(x_ticks), times_dynamic, label='Dynamic Strategy', marker='o')
plt.plot(list(x_ticks), times_random, label='Random Strategy', marker='x')
plt.xlabel('Task Count')
plt.ylabel('Task Completion Time (Time Units)')
plt.title('Comparison of Task Completion Time ')
plt.legend()
plt.grid(True)
save_plot_with_timestamp(save_dir, 'Total_Time_Comparison', plt.gcf())

# 决策准确性图
plt.figure(figsize=(10, 6))
plt.plot(list(x_ticks), accuracies_dynamic, label='Dynamic Strategy', marker='o')
plt.plot(list(x_ticks), accuracies_random, label='Random Strategy', marker='x')
plt.xlabel('Task Count')
plt.ylabel('Decision Accuracy (%)')
plt.ylim(0, 110)  # 设置Y轴范围为0到110
plt.title('Comparison of Decision Accuracy ')
plt.legend()
plt.grid(True)
save_plot_with_timestamp(save_dir, 'Accuracy_Comparison', plt.gcf())
