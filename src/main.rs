mod utils;
use std::{collections::HashMap, vec};

use utils::{*};

use crate::utils::graphs::CentralityGraph;

fn main() {
	let filename = "sample_graphs/J.5.1.json".to_string();
	let adj_list = parsing::adj_list_from_file(&filename).unwrap();
	println!("adj_list created");
	let nodes= sim::Sim::new(&adj_list);
	println!("nodes created");
	print!("Calculating graph shit");
	let mut graph = CentralityGraph::new(&filename, nodes);
	println!("cg created");
	// let our_seeds = graph.choose_seed_nodes_given_weights(&[1.0, 0.0, 0.0], 5);
	// let their_seeds = graph.choose_seed_nodes_given_weights(&[0.0, 1.0, 0.0], 5);
	let mut our_seeds = vec![];
	let mut their_seeds = vec![];

	for label in vec!["13", "2", "11", "92", "9", "8", "10", "75", "33", "17"] {
		our_seeds.push(graph.sim.nodes.iter().position(|node| node.label == label).unwrap());
	}

	for label in vec!["20", "7", "15", "80", "150", "40", "30", "25", "90", "1"] {
		their_seeds.push(graph.sim.nodes.iter().position(|node| node.label == label).unwrap());
	}

	println!("Seeds created");
	
	let mut seeds:HashMap<String, Vec<usize>> = HashMap::new();
	seeds.insert("our_seeds".to_string(), our_seeds);
	seeds.insert("their_seeds".to_string(), their_seeds);

	println!("Simulation Prepped and Starting");
	
	let counts = graph.sim.run(&seeds);

	println!("Simulation Over");
	println!("debug: {:#?}", counts);
}
