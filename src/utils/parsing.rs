use std::{collections::HashMap, io::{Read}, fs::File};
use serde_json::{Result};

pub fn adj_list_from_file(file_name: &String) -> Result<HashMap<String, Vec<String>>> {
	let mut file = File::open(file_name).unwrap();
	let mut contents = String::new();
	file.read_to_string(&mut contents);
	// parse json into adj_list
	let adj_list:HashMap<String, Vec<String>> = serde_json::from_str(&contents)?;
	Ok(adj_list)
}
