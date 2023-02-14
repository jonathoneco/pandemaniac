use core::num;
use std::collections::HashMap;
use rand::prelude::*;
use rayon::vec;

pub struct Node {
	pub idx: usize,

	pub label: String,
	neighbors: Vec<usize>,
	color: Option<usize>,
	neighbor_count: Vec<f64>,
	colored_neighbors: usize,
	
	// New values (updated at each iteration).
	new_neighbor_count: Vec<f64>,
	new_colored_neighbors: usize,
}

impl Node {
	pub fn new(label: String, idx: usize) -> Node {
		Node {
			idx,
			label,
			neighbors: Vec::new(),
			color: None,
			neighbor_count: vec![0.0; 0],
			colored_neighbors: 0,
			new_neighbor_count: vec![0.0; 0],
			new_colored_neighbors: 0,
		}
	}
	
	pub fn new_color(&mut self, color: usize) {
		self.color = Some(color);
		
	}
	
	pub fn remove_color(&mut self) {

		self.color = None;
	}
	
	
	pub fn update(&mut self) {
		self.neighbor_count = self.new_neighbor_count.clone();
		self.colored_neighbors = self.new_colored_neighbors;
	}
	
	pub fn reset(&mut self, num_colors: usize) {
		// Set current values.
		self.color = None;
		self.neighbor_count = vec![0.0; num_colors];
		self.new_neighbor_count = vec![0.0; num_colors];
		self.colored_neighbors = 0;
		self.new_colored_neighbors = 0;
	}
}

pub struct Sim {
	pub nodes: Vec<Node>,
	iter: usize,
	colors: Vec<usize>,
}

impl Sim {
	pub fn new(adj_list: &HashMap<String, Vec<String>>) -> Sim {
		let nodes = Self::create_nodes(adj_list);
		Sim {
			nodes,
			iter: 0,
			colors: vec![]
		}
	}
	
	pub fn run(&mut self, seeds: &HashMap<String, Vec<usize>>) -> HashMap<String, f64>  {
		let indexed_seeds:Vec<(usize, &Vec<usize>)> = seeds.keys().enumerate().map(|(idx, color)| (idx, &seeds[color])).collect();
		let num_colors = indexed_seeds.len();
		
		self.reset_nodes(num_colors);
		self.seed_nodes(&indexed_seeds);
		let max_rounds:usize = rand::thread_rng().gen_range(100..=200);
		self.iter = 0;
		let mut converged = false;

		let mut avg_growth = vec![0.0; num_colors];
		self.colors = vec![0; num_colors];
		while self.iter < max_rounds && !converged {
			let prev_colors = self.colors.clone();
			converged = self.iterate();
			self.iter += 1;
			for i in 0..num_colors {
				avg_growth[i] += (self.colors[i] - prev_colors[i]) as f64;
			}
		}
		for i in 0..num_colors {
			avg_growth[i] /= self.iter as f64;
		}
		println!("Converged in {} iterations.", self.iter);

		let mut total_counts = vec![0.0; num_colors];
		for node in &self.nodes {
			if let Some(color) = node.color {
				total_counts[color] += 1.0;
			}
		}

		return seeds.keys().enumerate().map(|(idx, color)| (color.clone(), avg_growth[idx])).collect();
	}

	pub fn create_nodes(adj_list: &HashMap<String, Vec<String>>) -> Vec<Node> {
		// Collect adj_list into a map of node labels to rc of nodes
		let label_to_idx: HashMap<String, usize> = adj_list.keys().into_iter().enumerate().map(|(idx, label)| (label.clone(), idx)).collect();
		let mut nodes: Vec<Node> = adj_list.keys().into_iter().enumerate().map(|(idx, label)| Node::new(label.clone(), idx)).collect();
		for node in &mut nodes {
			let neighbors = &adj_list[&node.label];
			for neighbor in neighbors {
				node.neighbors.push(label_to_idx[neighbor]);
			}
		}
		
		return nodes;
	}

	pub fn reset_nodes(&mut self, num_colors: usize) {
		for node in &mut self.nodes {
			node.reset(num_colors);
		}
	}

	// TODO: Finish swapping from references to global node array for easier parallelization and headache reading this fucking code
	// TODO: After I've woken up, it's 4:32 am lol
	pub fn seed_nodes(&mut self, indexed_seeds: &Vec<(usize, &Vec<usize>)>) {
		let mut conflicts: Vec<usize> = vec![];
		for (color, seeds) in indexed_seeds {
			for seed in *seeds {
				let node = &self.nodes[*seed];
				if let Some(_color) = node.color {
					conflicts.push(node.idx);
				} else {
					let node_idx = node.idx;
					self.new_node_color(node_idx, *color);
				}
			}
		}
		
		for node_idx in conflicts {
			self.remove_node_color(node_idx);
		}

		for node in &mut self.nodes {
			node.update();
		}
	}

	pub fn iterate(&mut self) -> bool {
		let mut converged = true;
		let mut to_update: Vec<usize> = Vec::new();

		for node_idx in 0..self.nodes.len() {
			if self.update_node_color(node_idx, &mut to_update) {
				converged = false;
			}
		}

		for idx in to_update {
			let node = &mut self.nodes[idx];
			node.update();
		}
		
		return converged;
	}

	pub fn new_node_color(&mut self, node: usize, color: usize) {
		let node = &mut self.nodes[node];
		node.new_color(color);

		for neighbor_idx in &node.neighbors.clone() {
			let mut neighbor = &mut self.nodes[*neighbor_idx];
			neighbor.new_neighbor_count[color] += 1.0;
			neighbor.new_colored_neighbors += 1;
		}
	}

	pub fn remove_node_color(&mut self, node: usize) {
		let node = &mut self.nodes[node];
		let node_color = node.color;
		if let Some(color) = node_color {
			node.remove_color();
			for neighbor_idx in &node.neighbors.clone() {
				let mut neighbor = &mut self.nodes[*neighbor_idx];
				neighbor.new_neighbor_count[color] -= 1.0;
				neighbor.new_colored_neighbors -= 1;
			}

		}
	}

	pub fn update_node_color(&mut self, node_idx: usize, to_update: &mut Vec<usize>) -> bool {
		let node = &self.nodes[node_idx];
		let node_color = node.color;
		let mut new_color = None;
		let mut max_count= 0.0;
		for (color, count) in node.neighbor_count.iter().enumerate() {
			if *count > max_count {
				new_color = Some(color);
				max_count = *count;
			}
		}
		
		if let Some(new_color) = new_color {
			if let Some(curr_color) = node.color {
				if node.neighbor_count[curr_color] + 1.5 > max_count {
					return false;
				}
			}
			
			if max_count > node.colored_neighbors as f64 / 2.0 {
					to_update.push(node.idx);
					for neighbor_idx in &node.neighbors.clone() {
						let mut neighbor = &mut self.nodes[*neighbor_idx];
						to_update.push(neighbor.idx);
						neighbor.new_neighbor_count[new_color] += 1.0;
						if let Some(curr_color) = node_color {
							neighbor.new_neighbor_count[curr_color] -= 1.0;
						} else {
							neighbor.new_colored_neighbors += 1;
						}
					}
					{
						if let Some(curr_color) = node_color {
							self.colors[curr_color] -= 1;
						}
						self.colors[new_color] += 1;
						let node = &mut self.nodes[node_idx];
						node.color = Some(new_color);
					}
					return true;
			}
		}
		false
	}
}
	