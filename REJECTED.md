<!-- REJECTED.md -->
# Rejected / Deferred Ideas

A record of design experiments and ideas that were explored but intentionally not pursued.


## 🐍 Snake_case API
<a id="rej02"></a>*REJ 02 — 2025-01-XX*

### Context
Originally planned to provide a snake_case API as the primary interface, with camelCase in a compatibility namespace. The goal was to provide a more Pythonic API while maintaining stdlib compatibility.

### Reason for Rejection
- **Complexity vs. value**: Maintaining dual APIs (snake_case and camelCase) with proper inheritance support requires bidirectional wrappers, which is complex and brittle
- **Inheritance issues**: If users override camelCase methods, internal snake_case calls won't use the override. If users override snake_case, internal camelCase calls won't use it. logging.Logger only uses camelCase interally. Proper bidirectional routing adds significant complexity
- **Scope creep**: The library is intended for apatehtic tools first, and this is not a feature we need and would take away time on primary projects.

### Decision
Stick with camelCase only, inherit directly from `logging.Logger`, maintain original function signatures, use compatibility mode for internal breaking changes or value-add features that significantly change behavior.


## ⚡ Level Registry for Performance Optimization
<a id="rej01"></a>*REJ 01 — 2025-11-20*

### Context
Considered implementing a centralized level registry to improve the performance of `getLevelName()` and `getLevelNumber()` by using fast dict lookups first before calling `logging.getLevelName()` or `getattr(logging, level_name)`. The proposed approach would have maintained an internal registry of all known log levels (dict mapping level names to integers and vice versa), automatically populated with standard library levels (DEBUG, INFO, WARNING, ERROR, CRITICAL), custom apathetic levels (TEST, TRACE, DETAIL, BRIEF, SILENT), and user-registered levels (via our `addLevelName()` method). This would use dict lookups (~0.041μs per call) instead of `logging.getLevelName()` (~0.063μs) or `getattr()` (~0.063μs).

### Reason for Rejection
- Not on the hot path: `getLevelName()` and `getLevelNumber()` are not called during normal logging operations (`logger.info()`, `logger.debug()`, etc. do not call these functions). They are only called in `logDynamic()` (less common than standard logging methods), `setLevel()` (called during setup, not on every log), and `useLevel()` (context manager, not on every log)
- Negligible performance difference: The measured difference between dict lookup and `getattr()` is approximately 22 nanoseconds per call (dict lookup: ~0.041μs, `getattr()`: ~0.063μs, difference: ~0.022μs)
- I/O dominates: The logging hot path is fundamentally limited by file/TTY I/O, which is orders of magnitude slower (file write: ~1-10μs / 1,000-10,000 nanoseconds, TTY write: ~10-100μs / 10,000-100,000 nanoseconds). The 22ns optimization is 0.02% of a single file write operation
- Code complexity: Maintaining a registry would add registry initialization and synchronization logic, need to keep registry in sync with `logging.addLevelName()` calls, additional code paths and potential for bugs, with no meaningful benefit for the added complexity
- Redundancy: Our custom levels are already accessible via `getattr(logging, 'TEST')` because `extend_logging_module()` → `addLevelName()` sets the attributes. The dict lookup was redundant

### Revisit If
- Profiling shows `getLevelName()` or `getLevelNumber()` are actually on a hot path
- Performance measurements show the 22ns difference becomes significant in real-world usage
- A compelling use case emerges where the optimization would provide measurable benefit


