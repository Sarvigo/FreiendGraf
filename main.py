import requests
import time
import networkx as nx
import scipy.cluster.hierarchy as sch
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import squareform
from draw import draw_mesure_G

token = 'vk1.a.6SAnvuJZYyK1FJRxpp8p0W7zEax3eqEI8mQ32x0pG1bN7iQBCP4sCv5hU2sMBRqo7HNSd2HRweDQkB8qbMUbNEumkjgl0YqQ9iwU89L0XroQFE-tSta13xne1XRM7BK4ozcLCxtW9r3OYlWkGWB2CnPAwAdNzAD59E7kT5Zoyn6iUNUHGAJE3ttGfGIshH_12r2FITqRoMbcGjWNLD54cA'
myId = '310019925'

# targetUids = '337827479, 17799835, 259683779, 108614674'


def get_mutual_friends(userId, targetUids):
    response = requests.get('https://api.vk.com/method/friends.getMutual',
                            params={
                                'access_token': token,
                                'v': '5.199',
                                'source_uid': userId,
                                'target_uids': targetUids
                            }
                            )

    data = response.json()
    return data


def get_profile_info(userId):
    response = requests.get('https://api.vk.com/method/account.getProfileInfo',
                            params={
                                'access_token': token,
                                'user_id': userId,
                                'v': '5.199'
                            }
                            )

    data = response.json()
    return data


def get_friends(userId):
    response = requests.get('https://api.vk.com/method/friends.get',
                            params={
                                'access_token': token,
                                'user_id': userId,
                                'order': 'hints',
                                'v': '5.199'
                            }
                            )

    data = response.json()
    return data


my_friends_response = get_friends(myId)

if my_friends_response.get('error') is not None:
    print(my_friends_response)
    exit(1)

my_friends = my_friends_response['response']['items']


def get_mutual_friends_batches(my_friends, myId):
    start_count = list(range(0, len(my_friends), 18))
    end_count = [x + 17 for x in start_count]

    # Уменьшаем последний элемент в end_count, если он выходит за пределы списка
    if end_count[-1] > len(my_friends):
        end_count[-1] = len(my_friends)

    mutual_friends_responses = []
    for i in range(len(start_count)):
        current_array = my_friends[start_count[i]:end_count[i]]
        str_current_array = ', '.join(map(str, current_array))

        time.sleep(1)
        friends_data_response = get_mutual_friends(myId, str_current_array)

        if friends_data_response.get('error') is not None:
            print(friends_data_response)
            continue

        friends_data = friends_data_response['response']

        mutual_friends_responses += friends_data

        print(i)

    return mutual_friends_responses


friends_data = get_mutual_friends_batches(my_friends, myId)

G = nx.Graph()

'''Удаляем меня'''
# G.add_node(myId)

# for my_friend in my_friends:
#     G.add_node(my_friend)
#     G.add_edge(myId, my_friend)

for friend in friends_data:
    common_friends = friend['common_friends']
    friend_id = friend['id']

    if not G.has_node(friend_id):
        G.add_node(friend_id)

    for common_friend_id in common_friends:
        if not G.has_edge(friend_id, common_friend_id):
            G.add_edge(friend_id, common_friend_id)

# Удаляем ноды у которых количество связей меньше 10
no_neighbors_nodes = [node for node in G.nodes() if G.degree(node) < 10]
G.remove_nodes_from(no_neighbors_nodes)

def similarity(node1, node2, G):
    distance = 1 / (1 + nx.shortest_path_length(G, node1, node2))
    return distance

# Создание матрицы сходства на основе метрики сходства
def similarity_matrix(G):
    nodes = list(G.nodes())
    n = len(nodes)
    S = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            sim = similarity(nodes[i], nodes[j], G)
            S[i, j] = sim
            S[j, i] = sim # Матрица сходства симметрична
    return S

S = similarity_matrix(G)

# Преобразование матрицы расстояний в сжатую форму
distances = nx.to_numpy_array(G)
#condensed_distances = squareform(distances)

# Выполнение иерархической кластеризации
#Z = sch.linkage(distances, method='ward')
Z = sch.linkage(S, method='average')
#Z = sch.linkage(distances, method='complete')
#Z = sch.linkage(distances, method='single')

def print_max_metrics(G):
    betweenness_centrality = nx.betweenness_centrality(G)
    max_betweenness_node = max(betweenness_centrality, key=betweenness_centrality.get)
    print('Метрика близости: ', max_betweenness_node)

    closeness_centrality = nx.closeness_centrality(G)
    max_closeness_node = max(closeness_centrality, key=closeness_centrality.get)
    print('Метрика посредничества: ', max_closeness_node)

    # Для расчета метрики нужно перевести MultiGraph в обычный граф
    simple_G = nx.Graph(G)
    eigenvector_centrality = nx.eigenvector_centrality(simple_G)
    max_eigenvector_node = max(eigenvector_centrality, key=eigenvector_centrality.get)
    print('Метрика собственного вектора: ', max_eigenvector_node)

    # Визуализация дендрограммы
    plt.figure(figsize=(10, 5))
    plt.title('Dendrogram')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    sch.dendrogram(Z)
    plt.show()

    # Визуализация матрицы сходства в виде тепловой карты
    plt.imshow(S, cmap='hot', interpolation='nearest')
    plt.colorbar()  # Добавляем цветовую шкалу
    plt.title('Similarity Matrix')
    plt.xlabel('Samples')
    plt.ylabel('Samples')
    plt.show()

print_max_metrics(G)

print(G)
draw_mesure_G(G, 'closeness')
