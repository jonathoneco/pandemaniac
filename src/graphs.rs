use::petgraph::prelude::*;

pub mod graphs {
  pub struct CentralityGraph {
    graph: Graph<i32, ()>,
    degree_cen: HashMap<NodeIndex, f64>,
    between_cen: HashMap<NodeIndex, f64>,
    close_cen: HashMap<NodeIndex, f64>
  }
  
  impl CentralityGraph {
    pub fn new(graph: Graph<i32, ()>) -> CentralityGraph {
      let degree_cen = degree_centrality(&graph);
      let between_cen = betweenness_centrality(&graph);
      let close_cen = closeness_centrality(&graph);
      CentralityGraph {
        graph,
        degree_cen,
        between_cen,
        close_cen
      }
    }
  }

  fn degree_centralities(graph: &Graph<i32, ()>) -> HashMap<NodeIndex, f64> {
    let mut degree_cen: HashMap<NodeIndex, f64> = HashMap::new();
    let num_nodes = graph.node_count();
    for node in graph.node_indices() {
      let degree = graph.neighbors(node).count();
      degree_cen.insert(node, degree as f64 / (num_nodes - 1) as f64);
    }
    degree_cen
  }

  fn betweenness_centrality(graph: &Graph<i32, ()>) -> HashMap<NodeIndex, f64> {
    let mut between_cen: HashMap<NodeIndex, f64> = HashMap::new();
    let num_nodes = graph.node_count();
    for node in graph.node_indices() {
      let mut num_shortest_paths = 0;
      let mut num_paths = 0;
      for source in graph.node_indices() {
        for target in graph.node_indices() {
          if source == target {
            continue;
          }
          let paths = petgraph::algo::all_simple_paths(graph, source, target, 0, None);
          for path in paths {
            num_paths += 1;
            if path.contains(&node) {
              num_shortest_paths += 1;
            }
          }
        }
      }
      between_cen.insert(node, num_shortest_paths as f64 / num_paths as f64);
    }
    between_cen
  }

  fn closeness_centrality(graph: &Graph<i32, ()>) -> HashMap<NodeIndex, f64> {
    let mut close_cen: HashMap<NodeIndex, f64> = HashMap::new();
    let num_nodes = graph.node_count();
    for node in graph.node_indices() {
      let mut total_distance = 0;
      for source in graph.node_indices() {
        for target in graph.node_indices() {
          if source == target {
            continue;
          }
          let distance = petgraph::algo::astar(graph, source, |n| n == target, |_| 1, |_| 0);
          if let Some((distance, _)) = distance {
            total_distance += distance;
          }
        }
      }
      close_cen.insert(node, total_distance as f64 / ((num_nodes - 1) * (num_nodes - 2)) as f64);
    }
    close_cen
  }

  pub fn choose_seed_nodes_given_weights(weights: &[f64], num_seeds: usize) -> Vec<NodeIndex> {
    for node in graph.node_indices() {
      centrality.insert(node, degree_cen[node] * weights[0] + between_cen[node] * weights[1] + close_cen[node] * weights[2]);
    }
    
    let mut nodes: Vec<NodeIndex> = centrality.keys().cloned().collect();
    nodes.sort_by(|a, b| centrality[b].partial_cmp(&centrality[a]).unwrap());
    nodes[..num_seeds].to_vec()
  }
}