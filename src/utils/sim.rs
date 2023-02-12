use std::collections::HashMap;
use std::collections::HashSet;
use rand::prelude::*;

pub struct Node {
	idx: usize,

	label: String,
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
	
	pub fn new_colors(&mut self, sim: &Vec<Node>, color: usize) {
		self.color = Some(color);
		
		for neighbor_idx in self.neighbors {
			let mut neighbor = &mut sim[neighbor_idx];
			neighbor.new_neighbor_count[color] += 1.0;
			neighbor.new_colored_neighbors += 1;
		}
	}
	
	pub fn remove_color(&mut self, sim: &Vec<Node>) {

		for neighbor_idx in self.neighbors {
			let mut neighbor = &mut sim[neighbor_idx];
			neighbor.new_neighbor_count[self.color.unwrap()] -= 1.0;
			neighbor.new_colored_neighbors -= 1;
		}

		self.color = None;
	}
	
	fn update_color(&mut self, sim: &Vec<Node>, to_update: &mut Vec<usize>) -> bool {
		let mut new_color = None;
		let mut max_count= 0.0;
		for (color, count) in self.neighbor_count.iter().enumerate() {
			if *count > max_count {
				new_color = Some(color);
				max_count = *count;
			}
		}
		
		if let Some(new_color) = new_color {
			if let Some(curr_color) = self.color {
				if self.neighbor_count[curr_color] + 1.5 > max_count {
					return false;
				}
			}
			
			if max_count > self.colored_neighbors as f64 / 2.0 {
					to_update.push(self.idx);
					for neighbor_idx in self.neighbors {
						let mut neighbor = &mut sim[neighbor_idx];
						to_update.push(neighbor.idx);
						neighbor.new_neighbor_count[new_color] += 1.0;
						if let Some(curr_color) = self.color {
							neighbor.new_neighbor_count[curr_color] -= 1.0;
						} else {
							neighbor.new_colored_neighbors += 1;
						}
					}
					self.color = Some(new_color);
					return true;
			}
		}
		false
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

pub fn sim(sim: &Vec<Node>, seeds: &HashMap<String, Vec<String>>) -> HashMap<String, f64>  {
	let indexed_seeds:Vec<(usize, &Vec<String>)> = seeds.keys().enumerate().map(|(idx, color)| (idx, &seeds[color])).collect();
	let num_colors = indexed_seeds.len();
	
	reset_nodes(nodes, num_colors);
	seed_nodes(nodes, &indexed_seeds);
	let max_rounds:isize = rand::thread_rng().gen_range(100..=200);
	let mut iter = 0;
	let mut converged = false;

	while iter < max_rounds && !converged {
		converged = iterate(nodes);
		iter += 1;
	}
	println!("Converged in {} iterations.", iter);

	let mut total_counts = vec![0.0; num_colors];
	for noderef in nodes.values() {
		let node = noderef.borrow();
		if let Some(color) = node.color {
			total_counts[color] += 1.0;
		}
	}

	return seeds.keys().enumerate().map(|(idx, color)| (color.clone(), total_counts[idx])).collect();
}

pub fn create_nodes(adj_list: &HashMap<String, Vec<String>>) -> HashMap<String, Rc<RefCell<Node>>> {
	// Collect adj_list into a map of node labels to rc of nodes
	let nodes: HashMap<String, Rc<RefCell<Node>>> = adj_list.keys().into_iter().map(|label| (label.clone(), Node::new(label.clone()))).collect();
	for label in adj_list.keys() {
		let mut node = nodes[label].borrow_mut();
		let neighbors = &adj_list[label];
		for neighbor in neighbors {
			node.neighbors.push(Rc::downgrade(&nodes[neighbor]));
		}
	}
	
	return nodes;
}

pub fn reset_nodes(nodes: &HashMap<String, Rc<RefCell<Node>>>, num_colors: usize) {
	for noderef in nodes.values() {
		let mut node = noderef.borrow_mut();
		node.reset(num_colors);
	}
}

// TODO: Finish swapping from references to global node array for easier parallelization and headache reading this fucking code
// TODO: After I've woken up, it's 4:32 am lol
pub fn seed_nodes(sim: &mut Vec<Node>, indexed_seeds: &Vec<(usize, &Vec<String>)>) {
	let mut conflicts: Vec<usize> = vec![];
	for (color, seeds) in indexed_seeds {
		for seed in *seeds {
			let mut node = sim[seed].borrow_mut();
			if let Some(_color) = node.color {
				conflicts.push(Rc::clone(&nodes[seed]));
			} else {
				node.new_color(*color);
			}
		}
	}
	
	for noderef in conflicts {
		let mut node = noderef.borrow_mut();
		node.remove_color();
	}

	for noderef in nodes.values() {
		let mut node = noderef.borrow_mut();
		node.update();
	}
}

pub fn iterate(sim: &mut Vec<Node>) -> bool {
	let mut converged = true;
	let mut to_update: Vec<usize> = Vec::new();

	for node in sim {
		if node.update_color(sim, &mut to_update) {
			converged = false;
		}
	}

	for idx in to_update {
		let mut node = &mut sim[idx];
		node.update();
	}
	
	return converged;
}