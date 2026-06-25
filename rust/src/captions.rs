//! Opus-style word-by-word caption *chunking* — the pure, unit-tested half of
//! `src/ycp/captions.py`. Groups whisper segments into 1-3 word chunks with
//! approximate per-word timing.
//!
//! The Pillow render + ffmpeg overlay half (`render_overlay`, `burn_captions`,
//! font fitting, the `captions:` creative knobs) is deliberately NOT here — it's
//! the separate "captions render" row in README.md (Pillow → image+cosmic-text).
use crate::srt::Segment;
use crate::util::round_to;

pub const MAX_WORDS: usize = 3;
pub const MIN_DWELL: f64 = 0.4; // seconds a chunk stays on screen, minimum

/// One word with approximate [start, end] timing.
#[derive(Debug, Clone, PartialEq)]
pub struct Word {
    pub text: String,
    pub start: f64,
    pub end: f64,
}

/// A 1-3 word group shown together, the active word highlighted at render time.
#[derive(Debug, Clone, PartialEq)]
pub struct Chunk {
    pub start: f64,
    pub end: f64,
    pub words: Vec<Word>,
}

impl Chunk {
    /// Space-joined chunk text (mirrors the Python `text` property).
    pub fn text(&self) -> String {
        self.words
            .iter()
            .map(|w| w.text.as_str())
            .collect::<Vec<_>>()
            .join(" ")
    }
}

/// Distribute a segment's [start, end] evenly across its words (approx word timing).
pub fn split_words(seg: &Segment) -> Vec<Word> {
    let toks: Vec<&str> = seg.text.split_whitespace().collect();
    if toks.is_empty() {
        return Vec::new();
    }
    let span = (seg.end - seg.start).max(0.01);
    let step = span / toks.len() as f64;
    toks.iter()
        .enumerate()
        .map(|(i, t)| Word {
            text: (*t).to_string(),
            start: round_to(seg.start + i as f64 * step, 3),
            end: round_to(seg.start + (i + 1) as f64 * step, 3),
        })
        .collect()
}

/// Group words into <=max_words chunks, non-overlapping, each held >= min_dwell.
pub fn build_chunks(segments: &[Segment], max_words: usize, min_dwell: f64) -> Vec<Chunk> {
    let words: Vec<Word> = segments.iter().flat_map(split_words).collect();
    let mut chunks = Vec::new();
    let mut cursor = 0.0_f64;
    let mut i = 0;
    while i < words.len() {
        let grp = &words[i..(i + max_words).min(words.len())];
        let start = grp[0].start.max(cursor);
        let end = grp[grp.len() - 1].end.max(start + min_dwell);
        chunks.push(Chunk {
            start: round_to(start, 3),
            end: round_to(end, 3),
            words: grp.to_vec(),
        });
        cursor = end; // cursor tracks the UN-rounded end, like the Python.
        i += max_words;
    }
    chunks
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn split_words_even_distribution() {
        let seg = Segment::new(0.0, 3.0, "one two three");
        let w = split_words(&seg);
        assert_eq!(w.len(), 3);
        assert_eq!(
            w[0],
            Word {
                text: "one".into(),
                start: 0.0,
                end: 1.0
            }
        );
        assert_eq!(
            w[1],
            Word {
                text: "two".into(),
                start: 1.0,
                end: 2.0
            }
        );
        assert_eq!(
            w[2],
            Word {
                text: "three".into(),
                start: 2.0,
                end: 3.0
            }
        );
        // empty text → no words.
        assert!(split_words(&Segment::new(0.0, 1.0, "")).is_empty());
    }

    #[test]
    fn build_chunks_groups_and_enforces_dwell() {
        // 4 words over 4s → two chunks of 3 + 1; second chunk held >= MIN_DWELL.
        let segs = vec![Segment::new(0.0, 4.0, "a b c d")];
        let chunks = build_chunks(&segs, MAX_WORDS, MIN_DWELL);
        assert_eq!(chunks.len(), 2);
        assert_eq!(chunks[0].text(), "a b c");
        assert_eq!(chunks[1].text(), "d");
        assert_eq!(chunks[0].start, 0.0);
        assert_eq!(chunks[0].end, 3.0);
        // last word spans 3.0..4.0, already > min_dwell from start.
        assert_eq!(chunks[1].start, 3.0);
        assert_eq!(chunks[1].end, 4.0);
    }

    #[test]
    fn build_chunks_min_dwell_extends_short_chunk() {
        // a single very short word must still be held MIN_DWELL.
        let segs = vec![Segment::new(0.0, 0.1, "hi")];
        let chunks = build_chunks(&segs, MAX_WORDS, MIN_DWELL);
        assert_eq!(chunks.len(), 1);
        assert_eq!(chunks[0].start, 0.0);
        assert_eq!(chunks[0].end, 0.4); // extended to min_dwell
    }
}
