"""
Network Tools - Consolidated network operations for AI agents
Provides unified network and web browser capabilities.
"""
from typing import Any, Dict, List
import json
import subprocess
import platform
import urllib.request
import urllib.parse
import os
import webbrowser

# Try to import Rust engine for high-performance network operations
try:
    from que_core_engine import rust_ping_host, rust_check_internet, rust_network_tools, rust_web_browser
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

def network_tools(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal network tools - replaces ping_host, download_file, http_request, check_internet, get_public_ip, open_website
    
    Args:
        action (str): Action to perform - 'ping', 'download', 'request', 'check_internet', 'public_ip', 'open_url'
        host (str): Host for ping operations
        url (str): URL for download/request/open operations
        path (str): Local path for download operations
        method (str): HTTP method for requests (GET, POST, etc.)
        
    Returns:
        Dict with operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    # Try Rust implementation first for performance
    if RUST_AVAILABLE:
        try:
            host = args.get("host")
            url = args.get("url")
            path = args.get("path")
            method = args.get("method")
            count = args.get("count")
            
            result_json = rust_network_tools(action, host, url, path, method, count)
            return json.loads(result_json)
        except Exception:
            # Fall back to Python implementation
            pass
    
    # Python fallback implementation
    try:
        if action == "ping":
            return _ping_host_impl(args)
        elif action == "download":
            return _download_file_impl(args)
        elif action == "request":
            return _http_request_impl(args)
        elif action == "check_internet":
            return _check_internet_impl(args)
        elif action == "public_ip":
            return _get_public_ip_impl(args)
        elif action == "open_url":
            return _open_website_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: ping, download, request, check_internet, public_ip, open_url"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Network operation failed: {str(e)}"}

def auto_web_search(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Intelligent web search tool - automatically searches, browses, and extracts answers
    
    Args:
        query (str): Search query or question
        search_engine (str): Search engine to use (google, bing, duckduckgo)
        max_results (int): Maximum number of results to process (default: 3)
        extract_content (bool): Whether to extract and analyze content (default: True)
        
    Returns:
        Dict with search results, extracted content, and AI-friendly summary
    """
    if not args or "query" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: query"}
    
    query = args["query"]
    search_engine = args.get("search_engine", "google")
    max_results = args.get("max_results", 3)
    extract_content = args.get("extract_content", True)
    
    try:
        # Step 1: Perform web search
        search_results = _perform_web_search(query, search_engine, max_results)
        
        if not search_results["success"]:
            return search_results
        
        # Step 2: Extract content from top results if requested
        extracted_data = []
        if extract_content:
            for result in search_results["result"]["results"][:max_results]:
                content = _extract_web_content(result["url"])
                if content["success"]:
                    extracted_data.append({
                        "url": result["url"],
                        "title": result["title"],
                        "snippet": result["snippet"],
                        "content": content["result"]["content"],
                        "word_count": content["result"]["word_count"]
                    })
        
        # Step 3: Generate AI-friendly summary
        summary = _generate_search_summary(query, extracted_data)
        
        return {
            "success": True,
            "result": {
                "query": query,
                "search_engine": search_engine,
                "search_results": search_results["result"]["results"],
                "extracted_content": extracted_data,
                "summary": summary,
                "total_sources": len(extracted_data),
                "method": "auto_web_search"
            },
            "error": None
        }
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Auto web search failed: {str(e)}"}

def web_browser(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Smart browser control - replaces open_website with browser automation
    
    Args:
        action (str): Action to perform - 'navigate', 'search', 'open', 'close'
        url (str): URL to navigate to
        query (str): Search query
        browser (str): Specific browser to use
        
    Returns:
        Dict with operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    # Try Rust implementation first for performance
    if RUST_AVAILABLE:
        try:
            url = args.get("url")
            query = args.get("query")
            search_engine = args.get("search_engine")
            browser = args.get("browser")
            
            result_json = rust_web_browser(action, url, query, search_engine, browser)
            return json.loads(result_json)
        except Exception:
            # Fall back to Python implementation
            pass
    
    # Python fallback implementation
    try:
        if action == "navigate":
            return _navigate_browser_impl(args)
        elif action == "search":
            return _search_browser_impl(args)
        elif action == "open":
            return _open_browser_impl(args)
        elif action == "close":
            return _close_browser_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: navigate, search, open, close"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Browser operation failed: {str(e)}"}

# Implementation helpers
def _ping_host_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Ping host implementation"""
    host = args.get("host")
    if not host:
        return {"success": False, "result": None, "error": "Missing required argument: host"}
    
    count = args.get("count", 4)
    
    # Use Rust implementation for better performance
    if RUST_AVAILABLE:
        try:
            result_json = rust_ping_host(host, count)
            return json.loads(result_json)
        except Exception:
            # Fall back to Python implementation
            pass
    
    # Python fallback implementation
    try:
        # Use system ping command
        if platform.system() == "Windows":
            cmd = ["ping", "-n", str(count), host]
        else:
            cmd = ["ping", "-c", str(count), host]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        # Parse ping output for statistics
        output_lines = result.stdout.split('\n')
        stats = {
            "packets_sent": count,
            "packets_received": 0,
            "packet_loss": 100.0,
            "min_time": None,
            "max_time": None,
            "avg_time": None
        }
        
        # Simple parsing for basic stats
        for line in output_lines:
            if "packets transmitted" in line or "Packets: Sent" in line:
                # Extract packet statistics
                if "received" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "received" and i > 0:
                            stats["packets_received"] = int(parts[i-1])
                            break
        
        if stats["packets_sent"] > 0:
            stats["packet_loss"] = ((stats["packets_sent"] - stats["packets_received"]) / stats["packets_sent"]) * 100
        
        return {
            "success": result.returncode == 0,
            "result": {
                "host": host,
                "count": count,
                "statistics": stats,
                "reachable": result.returncode == 0,
                "output": result.stdout
            },
            "error": result.stderr if result.returncode != 0 else None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to ping host: {str(e)}"}

def _download_file_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Download file implementation"""
    url = args.get("url")
    path = args.get("path")
    
    if not url or not path:
        return {"success": False, "result": None, "error": "Missing required arguments: url, path"}
    
    try:
        overwrite = args.get("overwrite", False)
        
        # Check if file exists
        if os.path.exists(path) and not overwrite:
            return {"success": False, "result": None, "error": f"File already exists: {path}. Use overwrite=true to replace."}
        
        # Create parent directories if needed
        parent_dir = os.path.dirname(path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        
        # Download file with progress tracking
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) / total_size)
                # Could add progress callback here
        
        urllib.request.urlretrieve(url, path, progress_hook)
        
        # Get file info
        file_size = os.path.getsize(path)
        
        return {
            "success": True,
            "result": {
                "url": url,
                "path": path,
                "size": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "action": "downloaded"
            },
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to download file: {str(e)}"}

def _http_request_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """HTTP request implementation"""
    url = args.get("url")
    if not url:
        return {"success": False, "result": None, "error": "Missing required argument: url"}
    
    try:
        import urllib.request
        import urllib.error
        
        method = args.get("method", "GET").upper()
        headers = args.get("headers", {})
        data = args.get("data")
        timeout = args.get("timeout", 30)
        
        # Prepare request
        req = urllib.request.Request(url)
        
        # Add headers
        for key, value in headers.items():
            req.add_header(key, value)
        
        # Add data for POST requests
        if data and method in ["POST", "PUT", "PATCH"]:
            if isinstance(data, dict):
                data = urllib.parse.urlencode(data).encode('utf-8')
            elif isinstance(data, str):
                data = data.encode('utf-8')
            req.data = data
        
        # Make request
        response = urllib.request.urlopen(req, timeout=timeout)
        
        # Read response
        response_data = response.read().decode('utf-8')
        
        return {
            "success": True,
            "result": {
                "url": url,
                "method": method,
                "status_code": response.getcode(),
                "headers": dict(response.headers),
                "content": response_data,
                "content_length": len(response_data)
            },
            "error": None
        }
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "result": {
                "url": url,
                "method": method,
                "status_code": e.code,
                "error_message": str(e)
            },
            "error": f"HTTP Error {e.code}: {str(e)}"
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to make HTTP request: {str(e)}"}

def _check_internet_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Check internet connectivity implementation"""
    # Use Rust implementation for better performance
    if RUST_AVAILABLE:
        try:
            result_json = rust_check_internet()
            return json.loads(result_json)
        except Exception:
            # Fall back to Python implementation
            pass
    
    # Python fallback implementation
    try:
        test_hosts = ["8.8.8.8", "1.1.1.1", "google.com"]
        connected = False
        results = []
        
        for host in test_hosts:
            try:
                if platform.system() == "Windows":
                    cmd = ["ping", "-n", "1", "-w", "3000", host]
                else:
                    cmd = ["ping", "-c", "1", "-W", "3", host]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                success = result.returncode == 0
                
                results.append({
                    "host": host,
                    "reachable": success
                })
                
                if success:
                    connected = True
                    
            except Exception:
                results.append({
                    "host": host,
                    "reachable": False
                })
        
        return {
            "success": True,
            "result": {
                "connected": connected,
                "tests": results,
                "method": "ping_test"
            },
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to check internet: {str(e)}"}

def _get_public_ip_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get public IP implementation"""
    try:
        # Try multiple IP services
        ip_services = [
            "https://api.ipify.org",
            "https://ipinfo.io/ip",
            "https://icanhazip.com"
        ]
        
        for service in ip_services:
            try:
                response = urllib.request.urlopen(service, timeout=10)
                ip = response.read().decode('utf-8').strip()
                
                return {
                    "success": True,
                    "result": {
                        "public_ip": ip,
                        "service": service
                    },
                    "error": None
                }
            except Exception:
                continue
        
        return {"success": False, "result": None, "error": "Could not determine public IP"}
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get public IP: {str(e)}"}

def _open_website_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Open website implementation"""
    url = args.get("url")
    if not url:
        return {"success": False, "result": None, "error": "Missing required argument: url"}
    
    try:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Open in default browser
        webbrowser.open(url)
        
        return {
            "success": True,
            "result": {
                "url": url,
                "action": "opened_in_browser"
            },
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to open website: {str(e)}"}

def _navigate_browser_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Navigate browser implementation"""
    url = args.get("url")
    if not url:
        return {"success": False, "result": None, "error": "Missing required argument: url"}
    
    try:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        browser_name = args.get("browser", "default")
        
        if browser_name == "default":
            webbrowser.open(url)
        else:
            # Try to open with specific browser
            try:
                browser = webbrowser.get(browser_name)
                browser.open(url)
            except webbrowser.Error:
                # Fall back to default browser
                webbrowser.open(url)
        
        return {
            "success": True,
            "result": {
                "url": url,
                "browser": browser_name,
                "action": "navigated"
            },
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to navigate browser: {str(e)}"}

def _search_browser_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Search browser implementation"""
    query = args.get("query")
    if not query:
        return {"success": False, "result": None, "error": "Missing required argument: query"}
    
    try:
        search_engine = args.get("search_engine", "google")
        
        # Build search URL
        if search_engine == "google":
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        elif search_engine == "bing":
            search_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        elif search_engine == "duckduckgo":
            search_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
        else:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        
        # Open search in browser
        webbrowser.open(search_url)
        
        return {
            "success": True,
            "result": {
                "query": query,
                "search_engine": search_engine,
                "search_url": search_url,
                "action": "search_opened"
            },
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to search: {str(e)}"}

def _open_browser_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Open browser implementation"""
    try:
        browser_name = args.get("browser", "default")
        url = args.get("url", "about:blank")
        
        if browser_name == "default":
            webbrowser.open(url)
        else:
            try:
                browser = webbrowser.get(browser_name)
                browser.open(url)
            except webbrowser.Error:
                webbrowser.open(url)
        
        return {
            "success": True,
            "result": {
                "browser": browser_name,
                "url": url,
                "action": "browser_opened"
            },
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to open browser: {str(e)}"}

def _close_browser_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Close browser implementation"""
    try:
        return {
            "success": False,
            "result": None,
            "error": "Browser closing not yet implemented - requires browser automation"
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to close browser: {str(e)}"}

# Auto web search implementation helpers
def _perform_web_search(query: str, search_engine: str, max_results: int) -> Dict[str, Any]:
    """Perform REAL web search using DuckDuckGo Instant Answer API"""
    try:
        import json
        
        # Use DuckDuckGo Instant Answer API (no API key required)
        api_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        req = urllib.request.Request(api_url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        results = []
        
        # Extract instant answer if available
        if data.get('Abstract'):
            results.append({
                "title": data.get('Heading', query),
                "url": data.get('AbstractURL', ''),
                "snippet": data.get('Abstract', ''),
                "source": "duckduckgo_instant"
            })
        
        # Extract related topics
        for topic in data.get('RelatedTopics', [])[:max_results-len(results)]:
            if isinstance(topic, dict) and topic.get('Text'):
                results.append({
                    "title": topic.get('Text', '')[:100] + "...",
                    "url": topic.get('FirstURL', ''),
                    "snippet": topic.get('Text', ''),
                    "source": "duckduckgo_related"
                })
        
        # If no results from API, try web scraping DuckDuckGo HTML
        if not results:
            results = _scrape_duckduckgo_html(query, max_results)
        
        return {
            "success": True,
            "result": {
                "search_url": api_url,
                "results": results[:max_results],
                "total_found": len(results)
            },
            "error": None
        }
        
    except Exception as e:
        # Fallback to HTML scraping if API fails
        try:
            results = _scrape_duckduckgo_html(query, max_results)
            return {
                "success": True,
                "result": {
                    "search_url": f"https://duckduckgo.com/?q={urllib.parse.quote(query)}",
                    "results": results,
                    "total_found": len(results)
                },
                "error": None
            }
        except Exception as e2:
            return {"success": False, "result": None, "error": f"Failed to perform web search: {str(e)} | Fallback error: {str(e2)}"}

def _scrape_duckduckgo_html(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Scrape DuckDuckGo HTML search results as fallback"""
    import re
    
    search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    req = urllib.request.Request(search_url, headers=headers)
    response = urllib.request.urlopen(req, timeout=15)
    html_content = response.read().decode('utf-8', errors='ignore')
    
    results = []
    
    # Parse DuckDuckGo HTML results
    # Look for result containers
    result_pattern = r'<div class="result__body">.*?<a.*?href="([^"]*)".*?class="result__title".*?>(.*?)</a>.*?<a.*?class="result__snippet".*?>(.*?)</a>'
    matches = re.findall(result_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for url, title, snippet in matches[:max_results]:
        # Clean up extracted text
        title = re.sub(r'<[^>]+>', '', title).strip()
        snippet = re.sub(r'<[^>]+>', '', snippet).strip()
        
        # Decode URL if it's a DuckDuckGo redirect
        if url.startswith('/l/?uddg='):
            try:
                url = urllib.parse.unquote(url.split('uddg=')[1])
            except:
                pass
        
        if url and title:
            results.append({
                "title": title,
                "url": url,
                "snippet": snippet,
                "source": "duckduckgo_html"
            })
    
    return results

def _parse_google_results(html_content: str, max_results: int) -> List[Dict[str, Any]]:
    """Parse Google search results from HTML"""
    import re
    
    results = []
    
    # Simple regex patterns for Google search results
    # This is a basic implementation - in production, you'd want more robust parsing
    title_pattern = r'<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h3>'
    snippet_pattern = r'<div[^>]*class="[^"]*VwiC3b[^"]*"[^>]*>(.*?)</div>'
    
    title_matches = re.findall(title_pattern, html_content, re.DOTALL | re.IGNORECASE)
    snippet_matches = re.findall(snippet_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for i, (url, title) in enumerate(title_matches[:max_results]):
        # Clean URL (remove Google redirect)
        if url.startswith('/url?q='):
            url = urllib.parse.unquote(url[7:].split('&')[0])
        
        # Clean title and snippet
        title = re.sub(r'<[^>]+>', '', title).strip()
        snippet = ""
        if i < len(snippet_matches):
            snippet = re.sub(r'<[^>]+>', '', snippet_matches[i]).strip()
        
        if url.startswith('http') and title:
            results.append({
                "title": title,
                "url": url,
                "snippet": snippet,
                "source": "google"
            })
    
    return results

def _parse_bing_results(html_content: str, max_results: int) -> List[Dict[str, Any]]:
    """Parse Bing search results from HTML"""
    import re
    
    results = []
    
    # Basic Bing result parsing
    result_pattern = r'<h2><a href="([^"]*)"[^>]*>(.*?)</a></h2>'
    matches = re.findall(result_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for url, title in matches[:max_results]:
        title = re.sub(r'<[^>]+>', '', title).strip()
        if url.startswith('http') and title:
            results.append({
                "title": title,
                "url": url,
                "snippet": "",
                "source": "bing"
            })
    
    return results

def _parse_duckduckgo_results(html_content: str, max_results: int) -> List[Dict[str, Any]]:
    """Parse DuckDuckGo search results from HTML"""
    import re
    
    results = []
    
    # Basic DuckDuckGo result parsing
    result_pattern = r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
    matches = re.findall(result_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for url, title in matches[:max_results]:
        title = re.sub(r'<[^>]+>', '', title).strip()
        if url.startswith('http') and title:
            results.append({
                "title": title,
                "url": url,
                "snippet": "",
                "source": "duckduckgo"
            })
    
    return results

def _extract_web_content(url: str) -> Dict[str, Any]:
    """Extract and clean REAL content from a web page"""
    try:
        if not url or not url.startswith('http'):
            return {"success": False, "result": None, "error": f"Invalid URL: {url}"}
        
        import re
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=15)
        
        # Handle gzip encoding
        content = response.read()
        if response.info().get('Content-Encoding') == 'gzip':
            import gzip
            content = gzip.decompress(content)
        
        html_content = content.decode('utf-8', errors='ignore')
        
        # Advanced text extraction
        # Remove script, style, and other non-content elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<nav[^>]*>.*?</nav>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<header[^>]*>.*?</header>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<footer[^>]*>.*?</footer>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Extract content from semantic elements first
        content_patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<main[^>]*>(.*?)</main>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*id="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<section[^>]*>(.*?)</section>',
        ]
        
        extracted_text = ""
        for pattern in content_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if matches:
                extracted_text = " ".join(matches)
                break
        
        # If no semantic content found, extract paragraphs and headings
        if not extracted_text.strip():
            p_matches = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL | re.IGNORECASE)
            h_matches = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', html_content, re.DOTALL | re.IGNORECASE)
            extracted_text = " ".join(h_matches + p_matches)
        
        # Clean up text
        extracted_text = re.sub(r'<[^>]+>', '', extracted_text)  # Remove remaining HTML tags
        extracted_text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', extracted_text)  # Remove HTML entities
        extracted_text = re.sub(r'\s+', ' ', extracted_text)  # Normalize whitespace
        extracted_text = extracted_text.strip()
        
        # Filter out navigation and boilerplate text
        lines = extracted_text.split('.')
        filtered_lines = []
        for line in lines:
            line = line.strip()
            # Skip short lines, navigation text, etc.
            if (len(line) > 20 and 
                not any(skip in line.lower() for skip in ['cookie', 'privacy policy', 'terms of service', 'subscribe', 'newsletter', 'advertisement'])):
                filtered_lines.append(line)
        
        extracted_text = '. '.join(filtered_lines)
        
        # Limit content length for AI processing
        max_length = 2000
        if len(extracted_text) > max_length:
            # Try to cut at sentence boundary
            sentences = extracted_text[:max_length].split('.')
            if len(sentences) > 1:
                extracted_text = '. '.join(sentences[:-1]) + '.'
            else:
                extracted_text = extracted_text[:max_length] + "..."
        
        word_count = len(extracted_text.split())
        
        # Validate that we got meaningful content
        if word_count < 10:
            return {"success": False, "result": None, "error": f"Insufficient content extracted from {url} (only {word_count} words)"}
        
        return {
            "success": True,
            "result": {
                "url": url,
                "content": extracted_text,
                "word_count": word_count,
                "content_length": len(extracted_text),
                "extraction_method": "real_html_parsing"
            },
            "error": None
        }
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to extract content from {url}: {str(e)}"}

def _generate_search_summary(query: str, extracted_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate AI-friendly summary of search results and extracted content"""
    try:
        if not extracted_data:
            return {
                "answer": "No content could be extracted from search results.",
                "confidence": "low",
                "sources_used": 0,
                "key_points": [],
                "total_words_analyzed": 0
            }
        
        # Combine all extracted content
        all_content = []
        total_words = 0
        sources_used = 0
        
        for data in extracted_data:
            if data["content"].strip():
                all_content.append(f"Source: {data['title']} ({data['url']})\n{data['content']}")
                total_words += data["word_count"]
                sources_used += 1
        
        combined_content = "\n\n".join(all_content)
        
        # Extract key sentences that might answer the query
        query_words = set(query.lower().split())
        sentences = []
        
        for content in all_content:
            # Split into sentences (basic approach)
            content_sentences = content.split('. ')
            for sentence in content_sentences:
                sentence = sentence.strip()
                if len(sentence) > 20:  # Filter out very short sentences
                    sentence_words = set(sentence.lower().split())
                    # Check if sentence contains query-related words
                    if query_words.intersection(sentence_words):
                        sentences.append(sentence)
        
        # Take top relevant sentences
        key_points = sentences[:5] if sentences else ["No directly relevant information found."]
        
        # Generate a simple answer summary
        if sentences:
            answer = f"Based on {sources_used} sources, here are the key findings about '{query}': " + " ".join(sentences[:3])
            confidence = "high" if sources_used >= 2 else "medium"
        else:
            answer = f"Limited information found about '{query}'. Please check the extracted content for more details."
            confidence = "low"
        
        return {
            "answer": answer,
            "confidence": confidence,
            "sources_used": sources_used,
            "key_points": key_points,
            "total_words_analyzed": total_words,
            "query_coverage": "good" if len(key_points) > 2 else "limited"
        }
        
    except Exception as e:
        return {
            "answer": f"Error generating summary: {str(e)}",
            "confidence": "error",
            "sources_used": 0,
            "key_points": [],
            "total_words_analyzed": 0
        }

# Legacy function aliases for backward compatibility
def ping_host(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use network_tools instead"""
    return network_tools(args={"action": "ping", **(args or {})})

def download_file(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use network_tools instead"""
    return network_tools(args={"action": "download", **(args or {})})

def http_request(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use network_tools instead"""
    return network_tools(args={"action": "request", **(args or {})})

def check_internet(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use network_tools instead"""
    return network_tools(args={"action": "check_internet", **(args or {})})

def get_public_ip(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use network_tools instead"""
    return network_tools(args={"action": "public_ip", **(args or {})})

def open_website(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use network_tools or web_browser instead"""
    return network_tools(args={"action": "open_url", **(args or {})})
