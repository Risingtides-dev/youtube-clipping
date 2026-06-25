//! `ycp` — YouTube clipping closed-loop ops (Rust port, in progress).
//! The Python in ../src/ycp stays the live system until this reaches parity.
mod config;
mod db;
mod util;

use std::collections::BTreeMap;

use anyhow::Result;
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "ycp", about = "YouTube clipping closed-loop ops")]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Create the database.
    Init,
    /// Clip counts by status + total views (reads the same data/clips.db).
    Status,
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let root = config::find_root()?;
    let conn = db::open(&config::db_path(&root))?;
    match cli.cmd {
        Cmd::Init => {
            println!("✓ database ready at {}", config::db_path(&root).display());
        }
        Cmd::Status => {
            let clips = db::clips_with_latest_metrics(&conn)?;
            let posted = clips.iter().filter(|c| c.status.as_deref() == Some("posted")).count();
            let views: i64 = clips.iter().map(|c| c.views).sum();
            println!("ycp (rust) · {}", root.display());
            println!("clips: {} total · {} posted · {} views", clips.len(), posted, views);
            let mut by: BTreeMap<String, usize> = BTreeMap::new();
            for c in &clips {
                *by.entry(c.status.clone().unwrap_or_default()).or_default() += 1;
            }
            for (status, n) in by {
                println!("  {status:<12} {n}");
            }
        }
    }
    Ok(())
}
