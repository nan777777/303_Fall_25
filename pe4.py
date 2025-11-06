from __future__ import annotations

import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List, Tuple

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError, HTTPTimeoutError

SEARCH_QUERY = "generative artificial intelligence"
MAX_TOPICS = 20           
OUTPUT_DIR = "pe4_refs"   
WIKI_LANG = "en"          
MAX_WORKERS = 10          

def safe_filename(name: str) -> str:
 
    name = re.sub(r"[\\/:*?\"<>|\t\n\r]", "_", name).strip()
    
    if len(name) > 180:
        name = name[:180].rstrip("_")
    return name or "untitled"


def write_lines(path: str, lines: Iterable[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(f"{line}\n")


def fetch_title_and_references(topic: str) -> Tuple[str, List[str]]:
    wikipedia.set_lang(WIKI_LANG)               
    page = wikipedia.page(topic, auto_suggest=False)
    title = page.title
    refs = [str(r) for r in page.references]     
    return title, refs


def wiki_dl_and_save(topic: str) -> Tuple[str, int, str]:
    try:
        title, refs = fetch_title_and_references(topic)
        filename = f"{safe_filename(title)}.txt"
        out_path = os.path.join(OUTPUT_DIR, filename)
        write_lines(out_path, refs)
        return title, len(refs), "ok"
    except DisambiguationError as e:
        # if ambiguous, record the options for transparency
        filename = f"{safe_filename(topic)}__DISAMBIGUATION.txt"
        out_path = os.path.join(OUTPUT_DIR, filename)
        write_lines(out_path, [f"Disambiguation for '{topic}'. Options:"] + list(e.options))
        return topic, 0, f"disambiguation({len(e.options)} options)"
    except PageError:
        return topic, 0, "page_not_found"
    except HTTPTimeoutError:
        return topic, 0, "timeout"
    except Exception as e:
        return topic, 0, f"error:{type(e).__name__}: {e}"


def sequential(topics: Iterable[str]) -> float:
    start = time.perf_counter()
    for t in topics:
        title, n, status = wiki_dl_and_save(t)
        print(f"[SEQ] {t!r} -> title={title!r}, refs={n}, status={status}")
    elapsed = time.perf_counter() - start
    print(f"[SEQ] Completed {len(list(topics)) if not isinstance(topics, list) else len(topics)} topics in {elapsed:.2f}s")
    return elapsed


def concurrent(topics: List[str], max_workers: int = MAX_WORKERS) -> float:
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for title, n, status in ex.map(wiki_dl_and_save, topics):
            print(f"[CON] title={title!r}, refs={n}, status={status}")
    elapsed = time.perf_counter() - start
    print(f"[CON] Completed {len(topics)} topics with {max_workers} workers in {elapsed:.2f}s")
    return elapsed


def pick_topics() -> List[str]:
    wikipedia.set_lang(WIKI_LANG)
    raw = wikipedia.search(SEARCH_QUERY)
    if MAX_TOPICS:
        raw = raw[:MAX_TOPICS]
    # guard empty
    if not raw:
        print("Wikipedia search returned no topics. Check your network or query.", file=sys.stderr)
    return raw


def main() -> None:
    print("=== PE4: Wikipedia References Downloader ===")
    print(f"Search query: {SEARCH_QUERY!r} (lang={WIKI_LANG})")
    topics = pick_topics()
    if not topics:
        sys.exit(2)
    print(f"Found {len(topics)} topic(s). Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print("\n--- Section A: Sequential ---")
    t1 = sequential(topics)

    print("\n--- Section B: Concurrent (ThreadPoolExecutor) ---")
    t2 = concurrent(topics, max_workers=MAX_WORKERS)

    print("\n=== Timing Summary ===")
    print(f"Sequential: {t1:.2f} s")
    print(f"Concurrent: {t2:.2f} s")
    if t2 > 0:
        print(f"Speedup (seq/conc): {t1 / t2:.2f}x")

if __name__ == '__main__':
    main()
