# Time Falsehoods

## Core Rules

- Preserve user intent separately from derived instants: store local date/time, time zone or calendar context, recurrence rules, and creation assumptions when future scheduling matters.
- Use maintained time-zone, calendar, and duration libraries; do not hand-roll offset or calendar arithmetic.
- Distinguish instants, civil dates, local times, durations, periods, recurring events, monotonic elapsed time, and display formats.
- Version and refresh time-zone data, and expect past and future interpretations to change.
- Validate date/time inputs in the target calendar and zone, then handle nonexistent and repeated local times explicitly.
- Use monotonic clocks for elapsed-time measurement and wall clocks for human time; do not substitute one for the other.
- Store enough context to re-render the original promise to the user, especially for appointments, deadlines, payroll, billing periods, and recurring events.
- Decide whether arithmetic means "add elapsed seconds" or "advance the calendar by one civil unit"; `+24 hours` and "tomorrow at the same local time" are different operations.
- Keep parsing strict at API boundaries and forgiving in user-facing entry only when you can show the interpreted value back to the user.
- Treat time-zone database updates as data migrations for future schedules and historical reports.

## Falsehoods To Avoid

- Days, weeks, months, and years are not fixed-length units; DST, leap days, leap seconds, calendar reforms, and political changes break simple arithmetic.
- Time zones are not stable offsets, do not change with generous notice, and do not all use one-hour DST transitions.
- UTC storage alone is not enough for future local events because the rules used to convert wall time can change.
- Unix time is not simply elapsed SI seconds since 1970 and can skip, repeat, smear, or move backward around leap-second handling and clock adjustment.
- Date formats are not universal; ISO week-year `YYYY`, calendar year `yyyy`, RFC 3339, ISO 8601, and human strings have distinct semantics.
- System clocks are not always correct, monotonic, synchronized, or close to real time.
- Calendar reform, time-zone abolition, and single-global-time proposals move complexity to humans and local institutions instead of removing it.
- Offsets are not zones. `-05:00` does not tell you DST rules, political changes, abbreviations, or future conversions.
- Abbreviations such as `CST`, `IST`, and `PST` are ambiguous and should not be used as canonical time-zone identifiers.
- Midnight and end-of-day are not harmless defaults; some days start with a skipped time, and inclusive/exclusive boundaries affect reporting.
- Month and year arithmetic is not reversible: adding one month to January 31 needs an explicit policy.
- Recurrence rules need a policy for skipped and repeated times, holidays, business days, locale calendars, and user moves between zones.
- Logs from multiple machines cannot be ordered safely by local wall time without clock synchronization, monotonic sequence IDs, or causal metadata.
- Time precision in storage and APIs can be seconds, milliseconds, microseconds, nanoseconds, ticks, or arbitrary decimals; truncation can break ordering and idempotency.
- Historical dates can use different calendars, missing days, local reforms, and retrospective corrections.
- "Now" is not stable within a request unless captured once and passed through.

## Edge Cases

- Some local times do not exist during spring-forward transitions; other local times occur twice during fall-back transitions.
- Australia/Lord_Howe has 30-minute DST shifts; historical zones include stranger offsets and date skips.
- `2014-12-28` can belong to ISO week 1 of 2015, depending on the week calendar being used.
- `23:59:60` can be a leap-second timestamp in systems that model leap seconds.
- The 1927 Shanghai offset example shows that historical time-zone data updates can change arithmetic results.
- Y2K, 2038, GPS rollovers, spreadsheet serial dates, and other critical dates are system-specific failure boundaries.
- A timestamp with no offset or zone is usually a local date-time, not an instant.
- A date-only value should not be converted through midnight UTC unless the business meaning really is an instant at UTC midnight.
- Leap-second smearing means two systems can both claim to use UTC while disagreeing during the smear window.
- Cron-style schedules can run zero, one, or two times across DST transitions unless the scheduler defines otherwise.
- Week numbers depend on week-start day, minimum days in first week, locale, and whether ISO week rules are used.
- Client and server clocks can disagree enough to break token expiry, cache freshness, upload ordering, and conflict resolution.
- Database and language libraries can use different time-zone data versions, causing inconsistent conversions in the same stack.

