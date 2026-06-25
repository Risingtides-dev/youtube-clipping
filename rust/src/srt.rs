//! Tiny SRT toolkit — parse Whisper output, then slice/shift it per clip.
//! Parity port of `src/ycp/srt.py`. Pure timing logic, unit-tested, no I/O beyond
//! what callers pass in.
use std::sync::OnceLock;

use regex::Regex;

use crate::util::round_to;

/// One subtitle segment, seconds-based. Mirrors the Python frozen dataclass.
#[derive(Debug, Clone, PartialEq)]
pub struct Segment {
    pub start: f64,
    pub end: f64,
    pub text: String,
}

impl Segment {
    pub fn new(start: f64, end: f64, text: impl Into<String>) -> Self {
        Self {
            start,
            end,
            text: text.into(),
        }
    }
}

fn ts_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"(\d\d):(\d\d):(\d\d)[,.](\d\d\d)").unwrap())
}

fn blank_split_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"\n\s*\n").unwrap())
}

/// Parse the first `HH:MM:SS,mmm` timestamp found in `s` to seconds; 0.0 if none.
fn parse_ts(s: &str) -> f64 {
    match ts_re().captures(s) {
        Some(c) => {
            let g = |i: usize| c[i].parse::<f64>().unwrap();
            g(1) * 3600.0 + g(2) * 60.0 + g(3) + g(4) / 1000.0
        }
        None => 0.0,
    }
}

/// Format seconds back to `HH:MM:SS,mmm` (bug-for-bug with Python `_fmt_ts`).
fn fmt_ts(t: f64) -> String {
    let t = t.max(0.0);
    let h = (t / 3600.0).floor() as i64;
    let m = ((t % 3600.0) / 60.0).floor() as i64;
    let s = (t % 60.0) as i64; // int(t % 60) — truncation toward zero (t >= 0)
    let ms = round_to((t - (t as i64 as f64)) * 1000.0, 0) as i64;
    format!("{h:02}:{m:02}:{s:02},{ms:03}")
}

/// Parse an SRT string into ordered Segments.
pub fn parse_srt(text: &str) -> Vec<Segment> {
    let trimmed = text.trim();
    let mut out = Vec::new();
    for block in blank_split_re().split(trimmed) {
        let lines: Vec<&str> = block.lines().filter(|ln| !ln.trim().is_empty()).collect();
        if lines.len() < 2 {
            continue;
        }
        let Some(ts_idx) = lines.iter().position(|ln| ln.contains("-->")) else {
            continue;
        };
        let ts_line = lines[ts_idx];
        let mut parts = ts_line.splitn(2, "-->");
        let left = parts.next().unwrap_or("");
        let right = parts.next().unwrap_or("");
        let body = lines[ts_idx + 1..].join(" ").trim().to_string();
        out.push(Segment::new(parse_ts(left), parse_ts(right), body));
    }
    out
}

/// Return segments overlapping [start, end], retimed to begin at 0.
pub fn slice_and_shift(segments: &[Segment], start: f64, end: f64) -> Vec<Segment> {
    segments
        .iter()
        .filter(|seg| !(seg.end <= start || seg.start >= end))
        .map(|seg| {
            Segment::new(
                seg.start.max(start) - start,
                seg.end.min(end) - start,
                seg.text.clone(),
            )
        })
        .collect()
}

/// Render Segments back to an SRT string.
pub fn to_srt(segments: &[Segment]) -> String {
    let body = segments
        .iter()
        .enumerate()
        .map(|(i, seg)| {
            format!(
                "{}\n{} --> {}\n{}",
                i + 1,
                fmt_ts(seg.start),
                fmt_ts(seg.end),
                seg.text
            )
        })
        .collect::<Vec<_>>()
        .join("\n\n");
    format!("{body}\n")
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = "1\n00:00:01,000 --> 00:00:02,500\nhello world\n\n2\n00:00:02,500 --> 00:00:05,000\nthis is a test\n";

    #[test]
    fn parses_and_roundtrips() {
        let segs = parse_srt(SAMPLE);
        assert_eq!(segs.len(), 2);
        assert_eq!(segs[0], Segment::new(1.0, 2.5, "hello world"));
        assert_eq!(segs[1], Segment::new(2.5, 5.0, "this is a test"));
        // to_srt then parse_srt must reproduce the segments.
        assert_eq!(parse_srt(&to_srt(&segs)), segs);
    }

    #[test]
    fn fmt_ts_matches_python() {
        assert_eq!(fmt_ts(1.0), "00:00:01,000");
        assert_eq!(fmt_ts(2.5), "00:00:02,500");
        assert_eq!(fmt_ts(3661.123), "01:01:01,123");
        assert_eq!(fmt_ts(-5.0), "00:00:00,000");
    }

    #[test]
    fn slice_and_shift_overlap_only_retimed() {
        let segs = parse_srt(SAMPLE);
        // window [2.0, 4.0] overlaps both; retimed to begin at 0.
        let sliced = slice_and_shift(&segs, 2.0, 4.0);
        assert_eq!(sliced.len(), 2);
        assert_eq!(sliced[0], Segment::new(0.0, 0.5, "hello world"));
        assert_eq!(sliced[1], Segment::new(0.5, 2.0, "this is a test"));
        // non-overlapping window → empty.
        assert!(slice_and_shift(&segs, 10.0, 20.0).is_empty());
    }
}
