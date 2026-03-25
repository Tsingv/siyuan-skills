# Auth and Config

## Configuration precedence

Read configuration in this order:
1. CLI flags
2. Environment variables
3. Project `.env`
4. Built-in defaults

## Supported configuration

- `SIYUAN_HOST`: defaults to `http://127.0.0.1:6806`
- `SIYUAN_TOKEN`: preferred direct API token
- `PASSWORD`: access auth code used to log in and fetch an API token
- `SIYUAN_TIMEOUT`: request timeout in seconds
- `SIYUAN_OUTPUT_FORMAT`: default CLI output format

## Authentication flow

1. Use `SIYUAN_TOKEN` directly when present
2. Otherwise try cached token from `~/.cache/siyuan-skill/token.json`
3. Otherwise use `PASSWORD` with `/api/system/loginAuth`
4. Fetch token via `/api/system/getConf`
5. Retry once if API returns auth-expired code

## Notes

- Python CLI replaces shell `source` workflow
- Cache location is user-scoped, not `/tmp`
- If both `SIYUAN_TOKEN` and `PASSWORD` exist, token wins
