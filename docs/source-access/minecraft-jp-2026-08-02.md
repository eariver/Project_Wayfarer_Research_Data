# minecraft.jp one-time source access review

**Reviewed:** 2026-08-02  
**Scope:** One-time expanded ranking trial only  
**Recurring collection:** Not approved

## Public endpoints checked

- `https://minecraft.jp/robots.txt`
- `https://minecraft.jp/terms`
- `https://minecraft.jp/servers/score`
- `https://minecraft.jp/servers/score/page:2`
- `https://minecraft.jp/servers/player`
- `https://minecraft.jp/servers/recent`

All six endpoints returned HTTP 200 during the dry-run probe from a GitHub-hosted Actions runner.

## robots.txt observation

The retrieved file contained content-signal explanations for search, AI input, and AI training. It did not contain a `User-agent`, `Disallow`, `Allow`, or `Crawl-delay` directive in the observed response.

Observed Raw SHA-256:

```text
8fa3036c68bfcbd32365f6225d24333264093b7cd38d306e106b4dbdc934fd5b
```

## Terms observation

The public terms page contains a general prohibition covering modification, combination, reverse engineering, and analysis of the service. The scope of that wording as applied to low-frequency extraction of publicly rendered ranking rows is not resolved by this repository.

Raw HTML changes between requests because Cloudflare email-protection values and script nonces are dynamic. The Collector therefore verifies normalized visible text under `#content`, preserving the terms body while excluding those dynamic values.

Observed normalized `#content` text SHA-256:

```text
eaf7f25eb6b95c2fa4804d73057f8ced6df6c6478846490817bc6231522fc041
```

## Trial decision

The repository owner explicitly authorized one unscheduled trial. The trial is restricted to:

- one fixed Run ID;
- six sequential HTTPS requests;
- a repository-identifying User-Agent;
- two seconds between requests;
- one bounded retry;
- a 30-second timeout;
- a 10 MiB response limit;
- Score ranks 1-30;
- Player ranks 1-20;
- Recent ranks 1-20;
- no direct Minecraft Server List Ping;
- no authenticated or non-public information;
- no recurring or scheduled execution.

The collector verifies the Raw robots hash and normalized terms-body hash before accessing ranking pages. A relevant source-policy change stops the run rather than being accepted automatically.

Recurring automated collection remains blocked pending an explicit interpretation and approval of source-use constraints.
