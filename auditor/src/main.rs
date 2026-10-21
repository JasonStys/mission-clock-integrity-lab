//! Bounded, dependency-free interval ordering auditor by Jason Stys.
//! Functions, Event fields and variable locations: docs/CODE_INDEX.md. No unsafe/network/time APIs.
use std::collections::{BTreeMap, BTreeSet};
use std::io::{self, Read};

/// Event contains identity, stream sequence, wall ns, symmetric bound ns and qualification.
#[derive(Clone, Debug)]
struct Event {
    id: i64,
    stream: i64,
    seq: i64,
    stamp: i64,
    bound: i64,
    valid: i64,
}

/// Parse only canonical decimal i64 values, never floating or overflowing timestamps.
fn number(tokens: &mut std::str::SplitAsciiWhitespace<'_>) -> Result<i64, String> {
    let text = tokens.next().ok_or("Missing integer")?;
    let value = text.parse::<i64>().map_err(|_| "Invalid integer")?;
    if value.to_string() != text {
        return Err("Noncanonical integer".into());
    }
    Ok(value)
}

/// Strictly bound bytes, rows, IDs, unique source sequences and arithmetic before comparison.
fn parse(text: &str) -> Result<Vec<Event>, String> {
    if text.len() > 65536 || !text.is_ascii() {
        return Err("Oversize or non-ASCII request".into());
    }
    let mut tokens = text.split_ascii_whitespace();
    if tokens.next() != Some("EVENTS1") {
        return Err("Protocol".into());
    }
    let count = number(&mut tokens)?;
    if !(1..=96).contains(&count) {
        return Err("Event count".into());
    }
    let mut events = Vec::new();
    let mut ids = BTreeSet::new();
    let mut sequences = BTreeSet::new();
    for _ in 0..count {
        let e = Event {
            id: number(&mut tokens)?,
            stream: number(&mut tokens)?,
            seq: number(&mut tokens)?,
            stamp: number(&mut tokens)?,
            bound: number(&mut tokens)?,
            valid: number(&mut tokens)?,
        };
        if !(0..=95).contains(&e.id)
            || !(0..=3).contains(&e.stream)
            || !(0..=600).contains(&e.seq)
            || !(-9_000_000_000_000..=9_000_000_000_000).contains(&e.stamp)
            || !(0..=20_000_000_000).contains(&e.bound)
            || !(0..=1).contains(&e.valid)
            || !ids.insert(e.id)
            || !sequences.insert((e.stream, e.seq))
        {
            return Err("Event contract".into());
        }
        events.push(e);
    }
    if tokens.next().is_some() {
        return Err("Trailing input".into());
    }
    Ok(events)
}

/// Closed intervals must be strictly separated; touching does not establish strict time order.
fn relation(a: &Event, b: &Event) -> u8 {
    if a.valid == 0 || b.valid == 0 {
        3
    } else if a.stamp + a.bound < b.stamp - b.bound {
        0
    } else if b.stamp + b.bound < a.stamp - a.bound {
        1
    } else {
        2
    }
}

/// Audit O(E²) pairs plus per-stream source-order regressions, keeping input arrival order explicit.
fn audit(events: &[Event]) -> String {
    let mut pairs = Vec::new();
    for (i, a) in events.iter().enumerate() {
        for b in events.iter().skip(i + 1) {
            pairs.push(format!("[{},{},{}]", a.id, b.id, relation(a, b)));
        }
    }
    let mut last = BTreeMap::new();
    let mut disorder = 0;
    for e in events {
        if last.get(&e.stream).is_some_and(|seq| e.seq < *seq) {
            disorder += 1;
        }
        last.insert(e.stream, e.seq);
    }
    let mut ordered = events.to_vec();
    ordered.sort_by_key(|e| (e.stream, e.seq));
    let mut regressions = Vec::new();
    for pair in ordered.windows(2) {
        if pair[0].stream == pair[1].stream && pair[1].stamp < pair[0].stamp {
            regressions.push(format!("[{},{}]", pair[0].id, pair[1].id));
        }
    }
    format!(
        "{{\"pairs\":[{}],\"arrival_disorder\":{},\"regressions\":[{}]}}",
        pairs.join(","),
        disorder,
        regressions.join(",")
    )
}

/// Read at most limit+1 bytes, fail closed with a generic error, and emit only numeric JSON.
fn main() {
    let mut text = String::new();
    let result = io::stdin()
        .take(65537)
        .read_to_string(&mut text)
        .map_err(|_| "Invalid UTF-8".to_string())
        .and_then(|_| parse(&text));
    match result {
        Ok(events) => println!("{}", audit(&events)),
        Err(_) => {
            eprintln!("Invalid bounded event request");
            std::process::exit(2);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    /// Make synthetic interval observations; no physical clock assumptions hidden in fixtures.
    fn event(stamp: i64, bound: i64) -> Event {
        Event {
            id: 0,
            stream: 0,
            seq: 0,
            stamp,
            bound,
            valid: 1,
        }
    }
    /// Independently known closed-interval endpoints, symmetry, unqualified and negative cases.
    #[test]
    fn interval_contracts() {
        assert_eq!(relation(&event(0, 2), &event(5, 2)), 0);
        assert_eq!(relation(&event(5, 2), &event(0, 2)), 1);
        assert_eq!(relation(&event(0, 2), &event(4, 2)), 2);
        let mut invalid = event(-10, 0);
        invalid.valid = 0;
        assert_eq!(relation(&invalid, &event(5, 0)), 3);
        assert_eq!(relation(&event(-9, 0), &event(-8, 0)), 0);
    }
    /// Truncation, duplicate identity/sequence, huge values, floats, extra tokens and bytes reject.
    #[test]
    fn parser_contracts() {
        for text in [
            "",
            "EVENTS1 0",
            "EVENTS1 97",
            "EVENTS1 +1",
            "EVENTS1 1 0 0 1 0 0 2",
            "EVENTS1 1 0 0 1 9000000000001 0 1",
            "EVENTS1 1 0 0 1 0 -1 1",
            "EVENTS1 1 0 0 1 0 0 1 extra",
            "EVENTS1 1 0 0 1 0.0 0 1",
            "EVENTS1 2 0 0 1 0 0 1 0 1 1 0 0 1",
            "EVENTS1 2 0 0 1 0 0 1 1 0 1 0 0 1",
            "EVENTS1 1 0 0 1 0 0 1 🕐",
        ] {
            assert!(parse(text).is_err(), "{text}");
        }
        assert!(parse(&"x".repeat(65537)).is_err());
        assert!(parse("EVENTS1 1 0 0 1 0 0 1").is_ok());
    }
    /// Arrival disorder is not wall regression; source sequence determines the latter.
    #[test]
    fn sequence_contracts() {
        let e = parse("EVENTS1 3 2 0 2 4 0 1 1 0 1 5 0 1 0 1 0 -2 0 1").unwrap();
        let result = audit(&e);
        assert!(result.contains("\"arrival_disorder\":1"));
        assert!(result.contains("\"regressions\":[[1,2]]"));
    }
}
