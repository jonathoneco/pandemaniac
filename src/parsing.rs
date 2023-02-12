use std::{fs::File, collections::HashMap};
use std::io::prelude::*;
use serde_json::{Result, Value};
use petgraph::prelude::*;
mod graphs;

pub mod parsing {
	pub fn adj_list_from_file(fileName: String) -> Result<Value> {
		let mut file = File::open(fileName)?;
		let mut contents = String::new();
		file.read_to_string(&mut contents)?;
		let adj_list: Value = serde_json::from_str(&contents)?;
		Ok(adj_list)
	}
	
	pub fn create_graph(adj_list: &HashMap<i32, Vec<i32>>) -> CentralityGraph {
		let mut G = centrality_graph::CentralityGraph::new();
		let mut G = Graph::<i32, ()>::new();
		for (u, neighbors) in adj_list.iter() {
			let u = G.add_node(*u);
			for neighbor in neighbors {
				let neighbor = G.add_node(*neighbor);
				G.add_edge(u, neighbor, ());
			}
		}
		CentralityGraph::new(G)
	}
	
}