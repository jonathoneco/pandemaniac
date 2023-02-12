use std::collections::HashMap;
use std::process::Command;
use serde_json::{Value, from_str};
use::petgraph::prelude::*;

pub struct CentralityGraph {
	nodes: Vec<String>,
	data: Vec<HashMap<String, f64>>
}

impl CentralityGraph {
	pub fn new(fileName: &String, nodes: Vec<String>) -> CentralityGraph {
		let data = run_python_script(fileName);
		CentralityGraph {
			nodes,
			data
		}
	}
	
	
	pub fn choose_seed_nodes_given_weights(&mut self, weights: &[f64], num_seeds: usize) -> Vec<String> {
		let mut centrality: HashMap<String, f64> = HashMap::new();
		for node in &self.nodes {
			centrality.insert(node.clone(), self.data[0][node] * weights[0] + self.data[1][node] * weights[1] + self.data[2][node] * weights[2]);
		}
		
		self.nodes.sort_by(|a, b| centrality[b].partial_cmp(&centrality[a]).unwrap());
		return self.nodes.iter().take(num_seeds).map(|x| x.clone()).collect();

	}
}


// TODO: Doesn't currently take into account clusters cause fuck me I guess
pub fn run_python_script(filename: &str) -> Vec<HashMap<String, f64>> {
	println!("debug: {:#?}", filename);
	let output = Command::new("python")
	.arg("graph.py")
	.arg(filename)
	.output()
	.expect("Failed to run Python script");
	println!("debug: {:#?}", output);
	let output_str = String::from_utf8(output.stdout).unwrap();
	println!("{}", &output_str);
	let data: Vec<HashMap<String, f64>> = from_str(&output_str).unwrap();
	return data;
}