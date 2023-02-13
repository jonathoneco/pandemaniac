use std::collections::HashMap;
use std::process::Command;
use serde_json::{from_str};
use super::sim::*;

pub struct CentralityGraph {
	pub sim: Sim,
	data: Vec<HashMap<String, f64>>
}

impl CentralityGraph {
	pub fn new(file_name: &String, sim: Sim) -> CentralityGraph {
		let data = run_python_script(file_name);
		CentralityGraph {
			sim,
			data
		}
	}
	
	
	pub fn choose_seed_nodes_given_weights(&mut self, weights: &[f64], num_seeds: usize) -> Vec<usize> {
		let mut centrality: HashMap<usize, f64> = HashMap::new();
		for node in &self.sim.nodes {
			centrality.insert(node.idx, self.data[0][&node.label] * weights[0] + self.data[1][&node.label] * weights[1] + self.data[2][&node.label] * weights[2]);
		}
		
		let mut sorted_centrality_idx = (0..self.sim.nodes.len()).into_iter().collect::<Vec<usize>>();
		sorted_centrality_idx.sort_by(|a, b| centrality[b].partial_cmp(&centrality[a]).unwrap());
		return sorted_centrality_idx.into_iter().take(num_seeds).collect();
	}
}


// TODO: Doesn't currently take into account clusters cause fuck me I guess
pub fn run_python_script(filename: &str) -> Vec<HashMap<String, f64>> {
	let output = Command::new("python")
	.arg("graph.py")
	.arg(filename)
	.output()
	.expect("Failed to run Python script");
	let output_str = String::from_utf8(output.stdout).unwrap();
	let data: Vec<HashMap<String, f64>> = from_str(&output_str).unwrap();
	return data;
}