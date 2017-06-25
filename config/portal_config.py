from config.reader import env
from urllib.parse import urlparse, ParseResult

APP_PORT: int = env.safe_parse_or_value('APP_PORT', 8080, int)
PORTAL_URL: ParseResult = env.safe_parse_string('PORTAL_URL', 'http://localhost:3000', urlparse)
