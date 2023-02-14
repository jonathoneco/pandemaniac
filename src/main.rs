mod utils;
use std::{collections::HashMap, sync::{Mutex, Arc}};

use rand::Rng;
use utils::{*};
use rayon::prelude::*;

use crate::utils::graphs::CentralityGraph;

fn main() {
	let filename = "sample_graphs/J.5.1.json".to_string();
	let adj_list = parsing::adj_list_from_file(&filename).unwrap();
	println!("adj_list created");
	let nodes= sim::Sim::new(&adj_list);
	let n = nodes.nodes.len();
	println!("nodes created");
	print!("Calculating graph shit");
	let mut graph = CentralityGraph::new(&filename, nodes);
	println!("cg created");
	let num_seeds = 5;
	let total_seeds = 100;
	let mut seeds: Vec<Vec<usize>> = vec![];
	let mut rng = rand::thread_rng();
	seeds.push(graph.choose_seed_nodes_given_weights(&[1.0, 0.0, 0.0], num_seeds));
	seeds.push(graph.choose_seed_nodes_given_weights(&[0.0, 1.0, 0.0], num_seeds));
	seeds.push(graph.choose_seed_nodes_given_weights(&[0.0, 0.0, 1.0], num_seeds));
	seeds.push(graph.choose_seed_nodes_given_weights(&[1.0, 1.0, 1.0], num_seeds));
	for _ in 0..total_seeds {
		seeds.push((0..num_seeds).map(|_| rng.gen_range(0..n)).collect::<Vec<usize>>());
	}

	let mut wins = vec![0; seeds.len()];

	for i in 0..total_seeds-1 {
		for j in i+1..total_seeds {
			print!("{} vs {} ", i, j);
			let our_seeds = &seeds[i];
			let their_seeds = &seeds[j];
			let mut seeds:HashMap<String, Vec<usize>> = HashMap::new();
			seeds.insert("our_seeds".to_string(), our_seeds.clone());
			seeds.insert("their_seeds".to_string(), their_seeds.clone());
			
			let counts = graph.sim.run(&seeds);
			if counts["our_seeds"] > counts["their_seeds"] {
				wins[i] += 1;
			} else if counts["their_seeds"] > counts["our_seeds"] {
				wins[j] += 1;
			}
		}
	}

	let mut max_idx = 0;
	for i in 0..total_seeds {
		if wins[i] > wins[max_idx] {
			max_idx = i;
		}
	}
	println!("Winning Seed Pos: {:?}", max_idx);
	println!("Winning Seed: {:?}", seeds[max_idx]);
	println!("Winning Seed Score: {:?}", wins[max_idx]);

	println!("Simulation Over");
}

// fn main() {
// 	let filename = "sample_graphs/J.5.1.json".to_string();
// 	let adj_list = parsing::adj_list_from_file(&filename).unwrap();
// 	println!("adj_list created");
// 	let nodes= sim::Sim::new(&adj_list);
// 	let n = nodes.nodes.len();
// 	println!("nodes created");
// 	print!("Calculating graph shit");
// 	let mut graph = CentralityGraph::new(&filename, nodes);
// 	println!("cg created");
// 	// let our_seeds = graph.choose_seed_nodes_given_weights(&[1.0, 0.0, 0.0], 5);
// 	// let their_seeds = graph.choose_seed_nodes_given_weights(&[0.0, 1.0, 0.0], 5);

// 	// Generate a random selection of seed nodes
// 	let num_seeds = 5;
// 	let total_seeds = 200;
// 	let mut seeds: Vec<Vec<usize>> = vec![];
// 	let mut rng = rand::thread_rng();
// 	for _ in 0..total_seeds {
// 		seeds.push((0..num_seeds).map(|_| rng.gen_range(0..n)).collect::<Vec<usize>>());
// 	}

// 	let mut seeds_combo: Vec<(usize, usize)> = vec![];
// 	let wins = vec![0; seeds.len()];
// 	let mut wins_ref = &wins;

// 	let seed_pair_combo = (0..seeds.len()).into_par_iter().map(|i| {
// 		(i..seeds.len()).into_par_iter().map(|j| {
// 			(i, j)
// 		}).collect::<Vec<(usize, usize)>>()
// 	}).flatten().collect::<Vec<(usize, usize)>>();
// 	// let graph_mutex = Arc::new(Mutex::new(graph));
// 	// let wins_mutex = Arc::new(Mutex::new(wins));
// 	(0..seed_pair_combo.len()).into_par_iter().map(move |i| {
// 		let (i, j) = seed_pair_combo[i];
// 		let our_seeds = &seeds[i];
// 		let their_seeds = &seeds[j];
// 		let mut seeds:HashMap<String, Vec<usize>> = HashMap::new();
// 		seeds.insert("our_seeds".to_string(), our_seeds.clone());
// 		seeds.insert("their_seeds".to_string(), their_seeds.clone());
		
// 		// let graph_mutex = graph_mutex.clone();
// 		// let mut graph = graph_mutex.lock().unwrap();
// 		let counts = graph.sim.run(&seeds);
// 		if counts["our_seeds"] > counts["their_seeds"] {
// 			// let wins_mutex = wins_mutex.clone();
// 			// let mut wins = wins_mutex.lock().unwrap();
// 			wins_ref[i] += 1;
// 		} else if counts["their_seeds"] > counts["our_seeds"] {
// 			// let wins_mutex = wins_mutex.clone();
// 			// let mut wins = wins_mutex.lock().unwrap();
// 			wins_ref[j] += 1;
// 		}
// 	});

// 	let mut max_idx = 0;
// 	// let wins = wins_mutex.lock().unwrap();
// 	for i in 0..num_seeds {
// 		if wins[i] > wins[max_idx] {
// 			max_idx = i;
// 		}
// 	}

// 	println!("debug: {:#?}", wins);	
// 	println!("debug: {:#?}", seeds[max_idx]);
// 	println!("debug: {:#?}", wins[max_idx]);
// 	println!("Simulation Over");
// }

