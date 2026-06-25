//! Small shared helpers.
use chrono::SecondsFormat;

/// UTC now as ISO-8601, second precision — matches the Python db.now().
pub fn utc_now_iso() -> String {
    chrono::Utc::now().to_rfc3339_opts(SecondsFormat::Secs, true)
}

pub fn today_iso() -> String {
    chrono::Utc::now().format("%Y-%m-%d").to_string()
}
