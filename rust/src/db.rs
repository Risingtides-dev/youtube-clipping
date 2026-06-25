//! SQLite layer — schema, migrations, models, and queries. Mirrors src/ycp/db.py.
//! Same on-disk database as the Python version (data/clips.db), so they interoperate
//! during the port.
use std::path::Path;

use anyhow::Result;
use rusqlite::{params, Connection};

pub const SCHEMA: &str = r#"
CREATE TABLE IF NOT EXISTS source_videos (
    video_id      TEXT PRIMARY KEY,
    creator       TEXT NOT NULL,
    channel_id    TEXT,
    title         TEXT,
    url           TEXT NOT NULL,
    views         INTEGER,
    published_at  TEXT,
    view_velocity REAL,
    lane          TEXT NOT NULL,
    status        TEXT DEFAULT 'queued',
    sourced_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS clips (
    clip_id         TEXT PRIMARY KEY,
    source_video_id TEXT,
    source_creator  TEXT,
    channel         TEXT NOT NULL,
    platform        TEXT NOT NULL,
    lane            TEXT NOT NULL,
    fmt             TEXT,
    hook_type       TEXT,
    length_sec      INTEGER,
    status          TEXT DEFAULT 'pending_qc',
    post_title      TEXT,
    post_id         TEXT,
    experiment_id   TEXT,
    variant         TEXT,
    post_url        TEXT,
    posted_at       TEXT,
    slack_ts        TEXT,
    created_at      TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS metrics (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id       TEXT NOT NULL,
    captured_at   TEXT NOT NULL,
    views         INTEGER DEFAULT 0,
    retention_pct REAL,
    swipe_away_pct REAL,
    rpm           REAL,
    ad_revenue    REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS qc_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id    TEXT NOT NULL,
    reviewer   TEXT,
    decision   TEXT NOT NULL,
    note       TEXT,
    decided_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS briefs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start TEXT NOT NULL,
    content    TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_metrics_clip ON metrics(clip_id);
CREATE INDEX IF NOT EXISTS idx_clips_status ON clips(status);
"#;

/// A clip joined to its most recent metrics snapshot (mirrors clips_with_latest_metrics).
#[derive(Debug, Clone, Default)]
pub struct ClipRow {
    pub clip_id: String,
    pub source_creator: Option<String>,
    pub channel: Option<String>,
    pub platform: Option<String>,
    pub fmt: Option<String>,
    pub hook_type: Option<String>,
    pub length_sec: Option<i64>,
    pub status: Option<String>,
    pub post_title: Option<String>,
    pub post_id: Option<String>,
    pub experiment_id: Option<String>,
    pub variant: Option<String>,
    pub post_url: Option<String>,
    pub posted_at: Option<String>,
    pub views: i64,
    pub retention_pct: Option<f64>,
    pub swipe_away_pct: Option<f64>,
    pub ad_revenue: f64,
}

pub fn now() -> String {
    // UTC, second precision (matches the Python isoformat(timespec="seconds")).
    crate::util::utc_now_iso()
}

pub fn open(path: &Path) -> Result<Connection> {
    if let Some(dir) = path.parent() {
        std::fs::create_dir_all(dir).ok();
    }
    let conn = Connection::open(path)?;
    conn.execute_batch("PRAGMA foreign_keys = ON")?;
    init(&conn)?;
    Ok(conn)
}

pub fn init(conn: &Connection) -> Result<()> {
    conn.execute_batch(SCHEMA)?;
    // Idempotent migrations for columns added after a db already existed.
    for col in ["post_title TEXT", "post_id TEXT", "experiment_id TEXT", "variant TEXT"] {
        let _ = conn.execute(&format!("ALTER TABLE clips ADD COLUMN {col}"), []);
    }
    Ok(())
}

const CLIP_SELECT: &str = "
    SELECT c.clip_id, c.source_creator, c.channel, c.platform, c.fmt, c.hook_type,
           c.length_sec, c.status, c.post_title, c.post_id, c.experiment_id, c.variant,
           c.post_url, c.posted_at,
           COALESCE(m.views, 0), m.retention_pct, m.swipe_away_pct, COALESCE(m.ad_revenue, 0)
    FROM clips c
    LEFT JOIN (
        SELECT t.* FROM metrics t
        JOIN (SELECT clip_id, MAX(id) mid FROM metrics GROUP BY clip_id) latest
          ON t.id = latest.mid
    ) m ON m.clip_id = c.clip_id";

fn row_to_clip(r: &rusqlite::Row) -> rusqlite::Result<ClipRow> {
    Ok(ClipRow {
        clip_id: r.get(0)?,
        source_creator: r.get(1)?,
        channel: r.get(2)?,
        platform: r.get(3)?,
        fmt: r.get(4)?,
        hook_type: r.get(5)?,
        length_sec: r.get(6)?,
        status: r.get(7)?,
        post_title: r.get(8)?,
        post_id: r.get(9)?,
        experiment_id: r.get(10)?,
        variant: r.get(11)?,
        post_url: r.get(12)?,
        posted_at: r.get(13)?,
        views: r.get(14)?,
        retention_pct: r.get(15)?,
        swipe_away_pct: r.get(16)?,
        ad_revenue: r.get(17)?,
    })
}

/// One row per clip joined to its latest metrics snapshot.
pub fn clips_with_latest_metrics(conn: &Connection) -> Result<Vec<ClipRow>> {
    let mut stmt = conn.prepare(CLIP_SELECT)?;
    let rows = stmt.query_map([], row_to_clip)?.collect::<rusqlite::Result<Vec<_>>>()?;
    Ok(rows)
}

/// Clips ready to post (auto-QC approved or human-approved/scheduled).
pub fn approved_clips(conn: &Connection) -> Result<Vec<ClipRow>> {
    let sql = format!("{CLIP_SELECT} WHERE c.status IN ('approved','scheduled')");
    let mut stmt = conn.prepare(&sql)?;
    let rows = stmt.query_map([], row_to_clip)?.collect::<rusqlite::Result<Vec<_>>>()?;
    Ok(rows)
}

pub fn set_clip_status(conn: &Connection, clip_id: &str, status: &str) -> Result<()> {
    conn.execute("UPDATE clips SET status=?1 WHERE clip_id=?2", params![status, clip_id])?;
    Ok(())
}
