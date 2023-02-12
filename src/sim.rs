use std::collections::HashMap;
use std::collections::HashSet;
use std::collections::BTreeMap;
use rand::prelude::*;

pub mod sim {
    pub fn run(adj_list: &HashMap<i32, HashSet<i32>>, node_mappings: &HashMap<i32, Vec<i32>>) -> HashMap<i32, i32> {
        run_simulation(adj_list, node_mappings)
    }
    
    fn run_simulation(adj_list: &HashMap<i32, HashSet<i32>>, node_mappings: &HashMap<i32, Vec<i32>>) -> HashMap<i32, i32> {
        let mut node_color: HashMap<i32, Option<i32>> = HashMap::new();
        for node in adj_list.keys() {
            node_color.insert(*node, None);
        }
        init(node_mappings, &mut node_color);
        let mut generation = 1;
        
        let mut prev: HashMap<i32, Option<i32>> = HashMap::new();
        let nodes: Vec<&i32> = adj_list.keys().collect();
        let max_rounds = thread_rng().gen_range(100..200);
        while !is_stable(generation, max_rounds, &prev, &node_color) {
            prev = node_color.clone();
            for node in nodes.iter() {
                let (changed, color) = update(adj_list, &mut prev, **node);
                if changed {
                    node_color.insert(**node, color);
                }
            }
            generation += 1;
        }
        
        get_result(&node_mappings.keys().cloned().collect(), &node_color)
    }
    
    fn init(color_nodes: &HashMap<i32, Vec<i32>>, node_color: &mut HashMap<i32, Option<i32>>) {
        for (color, nodes) in color_nodes {
            for node in nodes {
                if node_color[node].is_some() {
                    node_color.insert(*node, None);
                } else {
                    node_color.insert(*node, Some(*color));
                }
            }
        }
    }
    
    fn update(adj_list: &HashMap<i32, HashSet<i32>>, node_color: &mut HashMap<i32, Option<i32>>, node: i32) -> (bool, Option<i32>) {
        let neighbors = &adj_list[&node];
        let colored_neighbors: Vec<Option<i32>> = neighbors.iter().map(|x| node_color[x]).collect();
        let mut team_count: BTreeMap<Option<i32>, f64> = BTreeMap::new();
        for &color in &colored_neighbors {
            *team_count.entry(color).or_default() += 1.0;
        }
        if let Some(color) = node_color[&node] {
            *team_count.entry(Some(color)).or_default() += 1.5;
        }
        let most_common = team_count
        .iter()
        .max_by(|(_, a), (_, b)| a.partial_cmp(b).unwrap());
        if let Some((_, count)) = most_common {
            if *count > colored_neighbors.len() as f64 / 2.0 {
                return (true, most_common.unwrap().0.clone());
            }
        }
        
        (false, node_color[&node])
    }
    
    fn is_stable(generation: i32, max_rounds: i32, prev: &HashMap<i32, Option<i32>>, curr: &HashMap<i32, Option<i32>>) -> bool {
        if generation <= 1 || prev.is_empty() {
            return false;
        }
        if generation == max_rounds {
            return true;
        }
        for (node, color) in curr {
            if prev[node] != *color {
                return false;
            }
        }
        true
    }
    
    fn get_result(colors: &Vec<i32>, node_color: &HashMap<i32, Option<i32>>) -> HashMap<i32, i32> {
        let mut color_nodes: HashMap<i32, i32> = HashMap::new();
        for color in colors {
            color_nodes.insert(*color, 0);
        }
        for (_, color) in node_color {
            if let Some(color) = color {
                *color_nodes.get_mut(&color).unwrap() += 1;
            }
        }
        color_nodes
    }
    
    
}