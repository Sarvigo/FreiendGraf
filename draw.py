import plotly.graph_objects as go
import networkx as nx


def draw_mesure_G(G, centrality_measure=None):
    pos = nx.spring_layout(G)

    # Создание списка координат узлов для визуализации
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]

    # Создание списка для хранения информации об именах и фамилиях узлов
    node_names = [int(node) for node in G.nodes()]

    # Создание списка ребер для визуализации
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # Создание визуализации узлов
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_names,
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='RdYlGn_r',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Centrality',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    # Оценка центральности узлов
    if centrality_measure == 'betweenness':
        centrality_scores = nx.betweenness_centrality(G)
    elif centrality_measure == 'closeness':
        centrality_scores = nx.closeness_centrality(G)
    elif centrality_measure == 'eigenvector':
        G = nx.Graph(G)  # Преобразование мультиграфа в обычный граф для собственного вектора
        centrality_scores = nx.eigenvector_centrality(G)
    else:
        centrality_scores = None

    if centrality_scores:
        node_trace.marker.color = list(centrality_scores.values())

    # Создание визуализации ребер
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    # Создание фигуры и показ
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Graph of Friends Network',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    fig.show()
