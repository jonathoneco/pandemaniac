mod utils;
use std::collections::HashMap;

use petgraph::graph::EdgesConnecting;
use utils::{*, sim::seed_nodes};

use crate::utils::graphs::CentralityGraph;

fn main() {
	let filename = "sample_graphs/J.5.1.json".to_string();
	let adj_list = parsing::adj_list_from_file(&filename).unwrap();
	println!("adj_list created");
	let mut graph = CentralityGraph::new(&filename, adj_list.keys().cloned().collect());
	println!("cg created");
	let our_seeds = graph.choose_seed_nodes_given_weights(&[1.0, 1.0, 1.0], 5);
	let their_seeds = graph.choose_seed_nodes_given_weights(&[0.1, 0.6, 0.3], 5);

	println!("Seeds created");
	
	let mut nodes = sim::create_nodes(&adj_list);
	let mut seeds:HashMap<String, Vec<String>> = HashMap::new();
	seeds.insert("our_seeds".to_string(), our_seeds);
	seeds.insert("their_seeds".to_string(), their_seeds);

	println!("Simulation Prepped and Starting");
	
	let counts = sim::sim(&mut nodes, &seeds);

	println!("Simulation Over");
	println!("debug: {:#?}", counts);
}
