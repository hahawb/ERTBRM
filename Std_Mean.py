import matplotlib
matplotlib.use('Agg')  # Set the Agg backend, which should be set before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime

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
    total_task_time = max(nodes[idx]['time'] for idx in selection_indices)
    
    return sum(votes) > len(votes) / 2, total_task_time

# Main simulation loop
def run_simulation(num_runs=100, task_sizes=[100, 500, 1000]):
    for num_tasks in task_sizes:
        print(f"Results for {num_tasks} tasks:")
        time_savings = []
        accuracy_improvements = []
        for _ in range(num_runs):
            nodes_dynamic = initialize_nodes()
            nodes_random = initialize_nodes()
            total_correct_dynamic = 0
            total_correct_random = 0
            total_time_dynamic = 0
            total_time_random = 0
            for _ in range(num_tasks):
                task = generate_task()
                correct_dynamic, time_dynamic = execute_cumulative_tasks(nodes_dynamic, task, dynamic=True)
                correct_random, time_random = execute_cumulative_tasks(nodes_random, task, dynamic=False)
                total_correct_dynamic += correct_dynamic
                total_correct_random += correct_random
                total_time_dynamic += time_dynamic
                total_time_random += time_random
            time_savings.append((total_time_random - total_time_dynamic) / total_time_dynamic * 100)
            accuracy_improvements.append((total_correct_dynamic - total_correct_random) / total_correct_random * 100)
        
        print("Average Time Savings (%): Mean = {:.2f}, Std = {:.2f}".format(np.mean(time_savings), np.std(time_savings)))
        print("Average Accuracy Improvements (%): Mean = {:.2f}, Std = {:.2f}".format(np.mean(accuracy_improvements), np.std(accuracy_improvements)))

# Run the simulation for 100 and 1000 tasks
run_simulation() 