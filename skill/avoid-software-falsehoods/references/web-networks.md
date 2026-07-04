# Web and Network Falsehoods

## Core Rules

- Parse URLs, HTML, IP addresses, DNS names, IDNs, favicons, and HTTP semantics with mature libraries and explicit normalization rules.
- Design networked systems for latency, partial failure, retries, duplicate delivery, inconsistent state, redirects, caching, and hostile input.
- Separate presentation, transport, resource identity, origin/security boundary, and application semantics.
- Preserve raw inputs where useful, and compare only after documented canonicalization.
- Normalize only for the operation being performed. Security checks, cache keys, routing, display, and analytics can require different URL or host representations.
- Make retries idempotent with request IDs, dedupe stores, conditional writes, or explicit conflict handling.
- Treat remote metadata as untrusted, including headers, content types, filenames, redirects, HTML tags, DNS responses, and certificate names.
- Observe and bound network behavior: timeouts, backoff, circuit breakers, request size limits, redirect limits, and cache-control handling should be explicit.

## Falsehoods To Avoid

- Networks are not reliable, zero-latency, secure, homogeneous, ordered, exactly-once, or controlled by one administrator.
- IP addresses do not have one textual form; IPv4 can be written in surprising decimal/octal/hex forms and IPv6 has multiple compressions and embeddings.
- Domain names and IDNs are not simple ASCII labels; homographs, punycode, normalization, registry policy, and user-agent display rules matter.
- URLs are not just strings with protocol, host, path, and query; parsers disagree on authority, encoding, escaping, userinfo, fragments, and relative resolution.
- HTML is not XML, is not always well-formed, and has parser recovery behavior that affects security and extraction.
- REST APIs are not automatically stateless, stable, cacheable, discoverable, idempotent, versioned, or semantically aligned with HTTP methods.
- DNS is not instant or singular; caching, split horizon, CNAME chains, search domains, DNSSEC, resolver policy, and propagation delays all affect results.
- TLS certificate identity, HTTP Host, SNI, redirects, cookies, CORS, and same-origin policy are separate mechanisms that can disagree.
- HTTP status codes, methods, headers, and content negotiation are conventions with edge cases; real APIs often tunnel semantics in bodies or custom headers.
- A successful TCP connection does not mean the service is healthy, authenticated, authorized, current, or safe to retry.
- Caches can store errors, vary by header, ignore intent, revalidate, serve stale content, or be bypassed by intermediaries.
- HTML extraction can execute no JavaScript, some JavaScript, or too much JavaScript depending on crawler design; the visible page may not match fetched markup.
- User agents differ in URL parsing, IDN display, favicon discovery, redirect handling, cookie rules, and mixed-content behavior.

## Edge Cases

- Favicons may require HTML discovery, redirects, relative URLs, multiple sizes, MIME confusion, fallback paths, caching, and error handling. [W9]
- Distributed systems fail through timeouts, retries, split brain, clock skew, duplicate messages, stale reads, and partial commits.
- Different URL parsers can disagree about where the host starts, how escapes decode, or whether a string is valid.
- IDN homographs and mixed-script labels can render as visually similar but distinct names.
- IPv4 strings can appear as integers, octal-looking dotted quads, shortened forms, or embedded inside IPv6 addresses.
- Percent-decoding at the wrong layer can turn inert text into path traversal, query confusion, or authorization bypass.
- Redirect chains can change scheme, host, path, cookies, headers, and method; clients need a policy for each transition.
- REST pagination over mutable data can skip or duplicate resources if cursors do not encode sort position and filter context.
- API clients should handle rate limits, Retry-After, partial responses, schema additions, unknown enum values, and eventual consistency.
- Favicons can be declared in multiple link tags, Apple touch icons, web manifests, `/favicon.ico`, SVGs, PNGs, or invalid content-type responses. [W9]

## Recommended Libraries

- URLs: WHATWG URL parsers (the `URL` class in browsers and Node, Ada, `whatwg-url`) or strict RFC 3986 libraries, with one documented canonicalization per purpose [W8].
- IP addresses: standard-library types (`ipaddress` in Python, `net/netip` in Go, `std::net` in Rust) instead of regex matching [W3], [W4].
- Domains and IDNs: UTS-46/IDNA processing libraries plus the Public Suffix List for registrable-domain logic [W5].
- HTML: spec-compliant HTML5 parsers (parse5, html5lib, html5ever, lxml's html5parser) — never regex extraction [W6].
- HTTP resilience: clients with explicit timeouts, retry-with-backoff, and circuit breakers (tenacity, resilience4j, got/ky, Polly), with idempotency keys on retried writes.

## Sources

Citation keys resolve in [source-index.md](source-index.md).

- Networks and distributed systems: [W1], [W2]
- IP addresses, DNS, and IDNs: [W3], [W4], [W5]
- HTML and URLs: [W6], [W8]
- REST APIs: [W7]
- Favicons: [W9]
